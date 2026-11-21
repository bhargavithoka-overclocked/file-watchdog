"""Keeps a record of every run so the last one can be undone."""

from __future__ import annotations

import json
import shutil
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path

from .organizer import Move

JOURNAL_NAME = ".file-watchdog-journal.json"


@dataclass
class UndoResult:
    restored: int = 0
    problems: list[str] = field(default_factory=list)


class Journal:
    def __init__(self, root: Path):
        self.root = Path(root)
        self.path = self.root / JOURNAL_NAME

    def _read(self) -> list[dict]:
        if not self.path.exists():
            return []
        return json.loads(self.path.read_text())

    def _write(self, runs: list[dict]):
        if runs:
            self.path.write_text(json.dumps(runs, indent=2))
        else:
            self.path.unlink(missing_ok=True)

    def record(self, moves: list[Move]):
        if not moves:
            return
        runs = self._read()
        runs.append({
            "time": datetime.now().isoformat(timespec="seconds"),
            "moves": [{"from": str(m.source), "to": str(m.destination)} for m in moves],
        })
        self._write(runs)

    def last_run(self) -> dict | None:
        runs = self._read()
        return runs[-1] if runs else None

    def undo_last(self) -> UndoResult | None:
        runs = self._read()
        if not runs:
            return None

        last = runs.pop()
        result = UndoResult()
        for item in reversed(last["moves"]):
            current, original = Path(item["to"]), Path(item["from"])
            if not current.exists():
                result.problems.append(f"{current.name} is gone, skipped it")
                continue
            if original.exists():
                result.problems.append(f"{original.name} already exists, left the moved copy where it is")
                continue
            original.parent.mkdir(parents=True, exist_ok=True)
            shutil.move(str(current), str(original))
            result.restored += 1

        self._write(runs)
        self._remove_empty_folders(Path(item["to"]).parent for item in last["moves"])
        return result

    def _remove_empty_folders(self, folders):
        # walk up from each folder we created, stopping at the root
        for folder in set(folders):
            while folder != self.root and self.root in folder.parents:
                if not folder.is_dir() or any(folder.iterdir()):
                    break
                folder.rmdir()
                folder = folder.parent
