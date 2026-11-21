from file_watchdog.organizer import Organizer, unique_path


def make_files(folder, *names):
    for name in names:
        (folder / name).write_text(name)


def test_plan_does_not_touch_anything(tmp_path):
    make_files(tmp_path, "a.jpg", "b.pdf")
    moves = Organizer(tmp_path).plan()

    assert {m.category for m in moves} == {"Images", "Documents"}
    assert (tmp_path / "a.jpg").exists()
    assert not (tmp_path / "Images").exists()


def test_apply_moves_files_into_category_folders(tmp_path):
    make_files(tmp_path, "a.jpg", "b.pdf", "unknown.xyz")
    organizer = Organizer(tmp_path)
    organizer.apply(organizer.plan())

    assert (tmp_path / "Images" / "a.jpg").exists()
    assert (tmp_path / "Documents" / "b.pdf").exists()
    assert (tmp_path / "unknown.xyz").exists()


def test_folders_are_left_alone(tmp_path):
    (tmp_path / "photos.jpg").mkdir()
    assert Organizer(tmp_path).plan() == []


def test_existing_file_is_not_overwritten(tmp_path):
    (tmp_path / "Images").mkdir()
    (tmp_path / "Images" / "a.jpg").write_text("old")
    (tmp_path / "a.jpg").write_text("new")

    organizer = Organizer(tmp_path)
    done = organizer.apply(organizer.plan())

    assert done[0].destination.name == "a (1).jpg"
    assert (tmp_path / "Images" / "a.jpg").read_text() == "old"
    assert (tmp_path / "Images" / "a (1).jpg").read_text() == "new"


def test_unique_path_keeps_counting(tmp_path):
    make_files(tmp_path, "a.txt", "a (1).txt")
    assert unique_path(tmp_path / "a.txt").name == "a (2).txt"
    assert unique_path(tmp_path / "b.txt").name == "b.txt"
