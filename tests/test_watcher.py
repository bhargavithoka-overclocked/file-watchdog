from pathlib import Path

from file_watchdog.organizer import Organizer
from file_watchdog.watcher import SortOnArrival, is_partial, wait_until_stable


def make_handler(folder):
    moved = []
    handler = SortOnArrival(Organizer(folder), moved.append, stable_checks=1, check_interval=0.01)
    return handler, moved


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


def test_is_partial():
    assert is_partial(Path("movie.mp4.crdownload"))
    assert is_partial(Path("thing.PART"))
    assert not is_partial(Path("movie.mp4"))


def test_partial_downloads_are_left_alone(tmp_path):
    handler, moved = make_handler(tmp_path)
    (tmp_path / "report.pdf.crdownload").write_text("half a file")

    handler.handle(tmp_path / "report.pdf.crdownload")

    assert moved == []
    assert (tmp_path / "report.pdf.crdownload").exists()


def test_wait_until_stable(tmp_path):
    path = tmp_path / "a.bin"
    path.write_text("done")
    assert wait_until_stable(path, checks=2, interval=0.01)


def test_wait_gives_up_if_file_disappears(tmp_path):
    assert not wait_until_stable(tmp_path / "gone.bin", interval=0.01)
