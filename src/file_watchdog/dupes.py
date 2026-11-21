"""Finding duplicate files by content."""

from __future__ import annotations

import hashlib
import shutil
from collections import defaultdict
from pathlib import Path

from .organizer import Move, unique_path

CHUNK_SIZE = 1024 * 1024
DUPES_FOLDER = "_duplicates"


def file_hash(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as f:
        # read in chunks so big videos don't get loaded into memory
        while chunk := f.read(CHUNK_SIZE):
            digest.update(chunk)
    return digest.hexdigest()


class DuplicateFinder:
    """
    Groups files with identical content.

    Files are grouped by size first, which is cheap. Only files that share
    a size get hashed, so most files are never read at all.
    """

    def __init__(self, root: Path | str, recursive: bool = True, min_size: int = 1):
        self.root = Path(root).expanduser().resolve()
        self.recursive = recursive
        self.min_size = min_size

    def files(self):
        pattern = "**/*" if self.recursive else "*"
        for path in self.root.glob(pattern):
            if not path.is_file() or path.is_symlink():
                continue
            parts = path.relative_to(self.root).parts
            if any(part.startswith(".") for part in parts) or parts[0] == DUPES_FOLDER:
                continue
            yield path

    def find(self) -> list[list[Path]]:
        by_size = defaultdict(list)
        for path in self.files():
            size = path.stat().st_size
            if size >= self.min_size:
                by_size[size].append(path)

        groups = []
        for same_size in by_size.values():
            if len(same_size) < 2:
                continue
            by_hash = defaultdict(list)
            for path in same_size:
                by_hash[file_hash(path)].append(path)
            groups.extend(sorted(group) for group in by_hash.values() if len(group) > 1)

        return sorted(groups, key=lambda group: str(group[0]))


def pick_original(group: list[Path]) -> Path:
    """Keep the oldest file, it's most likely the 'real' one."""
    return min(group, key=lambda p: (p.stat().st_mtime, len(p.name), str(p)))


def move_extras(groups: list[list[Path]], root: Path) -> list[Move]:
    """Move every copy except the original into root/_duplicates."""
    target = root / DUPES_FOLDER
    target.mkdir(exist_ok=True)

    moves = []
    for group in groups:
        original = pick_original(group)
        for path in group:
            if path == original:
                continue
            destination = unique_path(target / path.name)
            shutil.move(str(path), str(destination))
            moves.append(Move(path, destination, DUPES_FOLDER))
    return moves


def wasted_bytes(groups: list[list[Path]]) -> int:
    return sum(group[0].stat().st_size * (len(group) - 1) for group in groups)
