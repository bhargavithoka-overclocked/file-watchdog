from file_watchdog.journal import JOURNAL_NAME, Journal
from file_watchdog.organizer import Organizer


def sort_folder(folder):
    organizer = Organizer(folder)
    moves = organizer.apply(organizer.plan())
    Journal(folder).record(moves)
    return moves


def test_undo_puts_files_back(tmp_path):
    (tmp_path / "a.jpg").write_text("x")
    (tmp_path / "b.pdf").write_text("y")
    sort_folder(tmp_path)

    result = Journal(tmp_path).undo_last()

    assert result.restored == 2
    assert (tmp_path / "a.jpg").exists()
    assert (tmp_path / "b.pdf").exists()
    # the empty category folders get cleaned up too
    assert not (tmp_path / "Images").exists()
    assert not (tmp_path / JOURNAL_NAME).exists()


def test_undo_only_reverts_last_run(tmp_path):
    (tmp_path / "a.jpg").write_text("x")
    sort_folder(tmp_path)
    (tmp_path / "b.pdf").write_text("y")
    sort_folder(tmp_path)

    Journal(tmp_path).undo_last()

    assert (tmp_path / "b.pdf").exists()
    assert (tmp_path / "Images" / "a.jpg").exists()


def test_undo_with_empty_journal(tmp_path):
    assert Journal(tmp_path).undo_last() is None


def test_undo_does_not_overwrite(tmp_path):
    (tmp_path / "a.jpg").write_text("original")
    sort_folder(tmp_path)
    (tmp_path / "a.jpg").write_text("a new file with the same name")

    result = Journal(tmp_path).undo_last()

    assert result.restored == 0
    assert len(result.problems) == 1
    assert (tmp_path / "a.jpg").read_text() == "a new file with the same name"
    assert (tmp_path / "Images" / "a.jpg").exists()
