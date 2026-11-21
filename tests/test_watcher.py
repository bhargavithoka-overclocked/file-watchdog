from file_watchdog.organizer import Organizer
from file_watchdog.watcher import SortOnArrival


def make_handler(folder):
    moved = []
    return SortOnArrival(Organizer(folder), moved.append), moved


def test_new_file_gets_sorted(tmp_path):
    handler, moved = make_handler(tmp_path)
    (tmp_path / "a.jpg").write_text("x")

    handler.handle(tmp_path / "a.jpg")

    assert (tmp_path / "Images" / "a.jpg").exists()
    assert moved[0].category == "Images"


def test_files_in_subfolders_are_ignored(tmp_path):
    handler, moved = make_handler(tmp_path)
    (tmp_path / "Images").mkdir()
    (tmp_path / "Images" / "a.jpg").write_text("x")

    handler.handle(tmp_path / "Images" / "a.jpg")

    assert moved == []


def test_unknown_files_stay(tmp_path):
    handler, moved = make_handler(tmp_path)
    (tmp_path / "thing.xyz").write_text("x")

    handler.handle(tmp_path / "thing.xyz")

    assert moved == []
    assert (tmp_path / "thing.xyz").exists()
