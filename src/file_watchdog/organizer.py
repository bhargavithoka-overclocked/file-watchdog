from __future__ import annotations

import fnmatch
import shutil
from dataclasses import dataclass
from pathlib import Path

from .rules import Rule, default_rules, find_category


@dataclass
class Move:
    source: Path
    destination: Path
    category: str


class Organizer:
    """Works out where each file in a folder should go, and moves it there."""

    def __init__(
        self,
        root: Path | str,
        rules: list[Rule] | None = None,
        ignore: list[str] | None = None,
    ):
        self.root = Path(root).expanduser().resolve()
        self.rules = rules or default_rules()
        self.ignore = ignore or []

    def should_skip(self, path: Path) -> bool:
        if not path.is_file():
            return True
        return any(fnmatch.fnmatch(path.name, pattern) for pattern in self.ignore)

    def destination_for(self, path: Path) -> Move | None:
        category = find_category(path, self.rules)
        if category is None:
            return None
        return Move(path, self.root / category / path.name, category)

    def plan(self) -> list[Move]:
        moves = []
        for path in sorted(self.root.iterdir()):
            if self.should_skip(path):
                continue
            move = self.destination_for(path)
            if move:
                moves.append(move)
        return moves

    def apply(self, moves: list[Move]) -> list[Move]:
        done = []
        for move in moves:
            move.destination.parent.mkdir(parents=True, exist_ok=True)
            target = unique_path(move.destination)
            shutil.move(str(move.source), str(target))
            done.append(Move(move.source, target, move.category))
        return done


def unique_path(path: Path) -> Path:
    """Return path if it's free, otherwise 'name (1).ext', 'name (2).ext', ..."""
    if not path.exists():
        return path
    counter = 1
    while True:
        candidate = path.with_name(f"{path.stem} ({counter}){path.suffix}")
        if not candidate.exists():
            return candidate
        counter += 1
