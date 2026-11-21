from typer.testing import CliRunner

from file_watchdog.cli import app

runner = CliRunner()


def test_sort_command(tmp_path):
    (tmp_path / "a.jpg").write_text("x")
    result = runner.invoke(app, ["sort", str(tmp_path)])

    assert result.exit_code == 0
    assert (tmp_path / "Images" / "a.jpg").exists()


def test_dry_run_moves_nothing(tmp_path):
    (tmp_path / "a.jpg").write_text("x")
    result = runner.invoke(app, ["sort", "--dry-run", str(tmp_path)])

    assert result.exit_code == 0
    assert "would move" in result.output
    assert (tmp_path / "a.jpg").exists()


def test_empty_folder(tmp_path):
    result = runner.invoke(app, ["sort", str(tmp_path)])
    assert "Nothing to sort" in result.output


def test_undo_command(tmp_path):
    (tmp_path / "a.jpg").write_text("x")
    runner.invoke(app, ["sort", str(tmp_path)])
    result = runner.invoke(app, ["undo", str(tmp_path)])

    assert result.exit_code == 0
    assert "Restored 1 file" in result.output
    assert (tmp_path / "a.jpg").exists()


def test_dupes_command(tmp_path):
    (tmp_path / "a.txt").write_text("same")
    (tmp_path / "b.txt").write_text("same")

    result = runner.invoke(app, ["dupes", str(tmp_path)])
    assert "2 copies" in result.output
    assert (tmp_path / "b.txt").exists()

    result = runner.invoke(app, ["dupes", "--move", str(tmp_path)])
    assert result.exit_code == 0
    assert len(list((tmp_path / "_duplicates").iterdir())) == 1

    # moving duplicates can be undone like a normal sort
    runner.invoke(app, ["undo", str(tmp_path)])
    assert (tmp_path / "a.txt").exists() and (tmp_path / "b.txt").exists()
    assert not (tmp_path / "_duplicates").exists()


def test_no_dupes(tmp_path):
    (tmp_path / "a.txt").write_text("one")
    result = runner.invoke(app, ["dupes", str(tmp_path)])
    assert "No duplicates" in result.output
