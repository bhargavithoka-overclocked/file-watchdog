from __future__ import annotations

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

    def __init__(self, root: Path | str, rules: list[Rule] | None = None):
        self.root = Path(root).expanduser().resolve()
        self.rules = rules or default_rules()

    def destination_for(self, path: Path) -> Move | None:
        category = find_category(path, self.rules)
        if category is None:
            return None
        return Move(path, self.root / category / path.name, category)

    def plan(self) -> list[Move]:
        moves = []
        for path in sorted(self.root.iterdir()):
            if not path.is_file():
                continue
            move = self.destination_for(path)
            if move:
                moves.append(move)
        return moves

    def apply(self, moves: list[Move]) -> list[Move]:
        for move in moves:
            move.destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.move(str(move.source), str(move.destination))
        return moves
