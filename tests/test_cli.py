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
