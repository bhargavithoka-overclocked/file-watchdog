import os

from file_watchdog.dupes import DuplicateFinder, file_hash, move_extras, pick_original, wasted_bytes


def test_file_hash_matches_for_same_content(tmp_path):
    a = tmp_path / "a.txt"
    b = tmp_path / "b.txt"
    a.write_text("hello")
    b.write_text("hello")
    assert file_hash(a) == file_hash(b)


def test_finds_duplicates_in_subfolders(tmp_path):
    (tmp_path / "sub").mkdir()
    (tmp_path / "photo.jpg").write_bytes(b"same bytes")
    (tmp_path / "sub" / "photo copy.jpg").write_bytes(b"same bytes")
    (tmp_path / "other.jpg").write_bytes(b"diff bytes")  # same size, different content

    groups = DuplicateFinder(tmp_path).find()

    assert len(groups) == 1
    assert {p.name for p in groups[0]} == {"photo.jpg", "photo copy.jpg"}


def test_not_recursive(tmp_path):
    (tmp_path / "sub").mkdir()
    (tmp_path / "a.txt").write_text("x")
    (tmp_path / "sub" / "b.txt").write_text("x")
    assert DuplicateFinder(tmp_path, recursive=False).find() == []


def test_empty_files_are_ignored(tmp_path):
    (tmp_path / "a.txt").touch()
    (tmp_path / "b.txt").touch()
    assert DuplicateFinder(tmp_path).find() == []


def test_oldest_file_is_kept(tmp_path):
    old, new = tmp_path / "new-name.txt", tmp_path / "copy.txt"
    old.write_text("x")
    new.write_text("x")
    os.utime(old, (1_000_000, 1_000_000))
    assert pick_original([old, new]) == old


def test_move_extras(tmp_path):
    for name in ("a.txt", "a copy.txt", "a copy 2.txt"):
        (tmp_path / name).write_text("same")
    os.utime(tmp_path / "a.txt", (1_000_000, 1_000_000))

    groups = DuplicateFinder(tmp_path).find()
    assert wasted_bytes(groups) == 8

    moves = move_extras(groups, tmp_path)

    assert len(moves) == 2
    assert (tmp_path / "a.txt").exists()
    assert sorted(p.name for p in (tmp_path / "_duplicates").iterdir()) == ["a copy 2.txt", "a copy.txt"]
    # running again shouldn't count the quarantined files
    assert DuplicateFinder(tmp_path).find() == []
