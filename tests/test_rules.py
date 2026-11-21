from pathlib import Path

from file_watchdog.rules import Rule, default_rules, find_category, normalize_ext


def test_normalize_ext():
    assert normalize_ext("PDF") == ".pdf"
    assert normalize_ext(".Jpg ") == ".jpg"


def test_rule_matching_ignores_case():
    rule = Rule("Images", {"jpg", ".PNG"})
    assert rule.matches(Path("holiday.JPG"))
    assert rule.matches(Path("screenshot.png"))
    assert not rule.matches(Path("notes.txt"))


def test_default_categories():
    rules = default_rules()
    assert find_category(Path("report.pdf"), rules) == "Documents"
    assert find_category(Path("song.mp3"), rules) == "Audio"
    assert find_category(Path("backup.tar.gz"), rules) == "Archives"


def test_unknown_extension_has_no_category():
    assert find_category(Path("mystery.xyz"), default_rules()) is None
    assert find_category(Path("Makefile"), default_rules()) is None


def test_first_matching_rule_wins():
    rules = [Rule("Receipts", {".pdf"})] + default_rules()
    assert find_category(Path("invoice.pdf"), rules) == "Receipts"
