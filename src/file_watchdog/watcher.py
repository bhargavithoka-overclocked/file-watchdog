"""Watch a folder and sort files as soon as they show up."""

from __future__ import annotations

import os
import time
from pathlib import Path
from typing import Callable

from watchdog.events import FileSystemEvent, FileSystemEventHandler
from watchdog.observers import Observer

from .organizer import Move, Organizer

# temp names browsers and download tools use while a file is still coming in
PARTIAL_SUFFIXES = {".crdownload", ".part", ".partial", ".download", ".tmp"}


def is_partial(path: Path) -> bool:
    return path.suffix.lower() in PARTIAL_SUFFIXES


def wait_until_stable(path: Path, checks: int = 3, interval: float = 1.0, timeout: float = 600) -> bool:
    """
    Wait until a file stops growing (same size `checks` times in a row).
    Returns False if the file disappears or we give up waiting.
    """
    last_size = -1
    same = 0
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        try:
            size = path.stat().st_size
        except FileNotFoundError:
            return False
        if size == last_size:
            same += 1
            if same >= checks:
                return True
        else:
            same = 0
            last_size = size
        time.sleep(interval)
    return False


class SortOnArrival(FileSystemEventHandler):
    def __init__(
        self,
        organizer: Organizer,
        on_move: Callable[[Move], None],
        stable_checks: int = 3,
        check_interval: float = 1.0,
    ):
        self.organizer = organizer
        self.on_move = on_move
        self.stable_checks = stable_checks
        self.check_interval = check_interval

    def on_created(self, event: FileSystemEvent):
        if not event.is_directory:
            self.handle(Path(os.fsdecode(event.src_path)))

    def on_moved(self, event: FileSystemEvent):
        # Chrome and Firefox rename "file.pdf.crdownload" to "file.pdf" when done
        if not event.is_directory:
            self.handle(Path(os.fsdecode(event.dest_path)))

    def handle(self, path: Path):
        # only look at files dropped straight into the watched folder,
        # not the ones we just moved into the category folders
        if path.parent.resolve() != self.organizer.root:
            return
        if is_partial(path) or self.organizer.should_skip(path):
            return
        if not wait_until_stable(path, self.stable_checks, self.check_interval):
            return

        move = self.organizer.destination_for(path)
        if move is None:
            return
        done = self.organizer.apply([move])
        self.on_move(done[0])


def watch(organizer: Organizer, on_move: Callable[[Move], None]):
    """Block and sort new files until Ctrl+C."""
    observer = Observer()
    observer.schedule(SortOnArrival(organizer, on_move), str(organizer.root), recursive=False)
    observer.start()
    try:
        while observer.is_alive():
            observer.join(1)
    except KeyboardInterrupt:
        pass
    finally:
        observer.stop()
        observer.join()
