from pathlib import Path

import pytest

from file_watchdog.config import ConfigError, find_config, load_config
from file_watchdog.organizer import Organizer
from file_watchdog.rules import find_category


def write_config(folder, text):
    path = folder / "file-watchdog.toml"
    path.write_text(text)
    return path


def test_no_config_uses_defaults():
    config = load_config(None)
    assert config.ignore == []
    assert any(rule.category == "Images" for rule in config.rules)


def test_custom_categories_go_first(tmp_path):
    path = write_config(tmp_path, '[categories]\nReceipts = [".pdf"]\nBooks = ["epub"]\n')
    config = load_config(path)

    assert find_category(Path("x.pdf"), config.rules) == "Receipts"
    assert find_category(Path("x.epub"), config.rules) == "Books"
    assert find_category(Path("x.jpg"), config.rules) == "Images"


def test_replace_defaults(tmp_path):
    path = write_config(tmp_path, 'replace_defaults = true\n[categories]\nBooks = [".epub"]\n')
    config = load_config(path)
    assert [rule.category for rule in config.rules] == ["Books"]


def test_find_config_in_folder(tmp_path):
    path = write_config(tmp_path, "")
    assert find_config(tmp_path) == path


def test_bad_toml_raises(tmp_path):
    path = write_config(tmp_path, "this is = = not toml")
    with pytest.raises(ConfigError):
        load_config(path)


def test_extensions_must_be_a_list(tmp_path):
    path = write_config(tmp_path, '[categories]\nBooks = ".epub"\n')
    with pytest.raises(ConfigError):
        load_config(path)


def test_ignore_patterns(tmp_path):
    for name in ("keep.pdf", "draft-1.pdf", "photo.jpg"):
        (tmp_path / name).write_text("x")

    path = write_config(tmp_path, 'ignore = ["draft-*", "*.jpg"]\n')
    config = load_config(path)
    moves = Organizer(tmp_path, config.rules, config.ignore).plan()

    assert [m.source.name for m in moves] == ["keep.pdf"]
