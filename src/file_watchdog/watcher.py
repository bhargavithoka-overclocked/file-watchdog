"""Watch a folder and sort files as soon as they show up."""

from __future__ import annotations

import os
from pathlib import Path
from typing import Callable

from watchdog.events import FileSystemEvent, FileSystemEventHandler
from watchdog.observers import Observer

from .organizer import Move, Organizer


class SortOnArrival(FileSystemEventHandler):
    def __init__(self, organizer: Organizer, on_move: Callable[[Move], None]):
        self.organizer = organizer
        self.on_move = on_move

    def on_created(self, event: FileSystemEvent):
        if not event.is_directory:
            self.handle(Path(os.fsdecode(event.src_path)))

    def handle(self, path: Path):
        # only look at files dropped straight into the watched folder,
        # not the ones we just moved into the category folders
        if path.parent.resolve() != self.organizer.root:
            return
        if self.organizer.should_skip(path):
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
