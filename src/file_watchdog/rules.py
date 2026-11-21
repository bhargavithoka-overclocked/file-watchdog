"""Categories and the file extensions that belong to each one."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

DEFAULT_CATEGORIES: dict[str, list[str]] = {
    "Images": [".jpg", ".jpeg", ".png", ".gif", ".webp", ".heic", ".bmp", ".tiff", ".svg"],
    "Videos": [".mp4", ".mov", ".mkv", ".avi", ".webm", ".m4v"],
    "Audio": [".mp3", ".wav", ".flac", ".aac", ".m4a", ".ogg"],
    "Documents": [".pdf", ".doc", ".docx", ".txt", ".rtf", ".odt", ".md", ".pages"],
    "Spreadsheets": [".xls", ".xlsx", ".csv", ".ods", ".numbers"],
    "Presentations": [".ppt", ".pptx", ".key", ".odp"],
    "Archives": [".zip", ".tar", ".gz", ".tgz", ".rar", ".7z", ".bz2", ".xz"],
    "Code": [
        ".py", ".ipynb", ".js", ".ts", ".html", ".css", ".java", ".c", ".cpp",
        ".go", ".rs", ".json", ".yaml", ".yml", ".sh", ".sql",
    ],
    "Installers": [".dmg", ".pkg", ".exe", ".msi", ".deb", ".apk"],
    "Fonts": [".ttf", ".otf", ".woff", ".woff2"],
}


def normalize_ext(ext: str) -> str:
    ext = ext.strip().lower()
    return ext if ext.startswith(".") else "." + ext


@dataclass
class Rule:
    category: str
    extensions: set[str] = field(default_factory=set)

    def __post_init__(self):
        self.extensions = {normalize_ext(e) for e in self.extensions}

    def matches(self, path: Path) -> bool:
        return path.suffix.lower() in self.extensions


def default_rules() -> list[Rule]:
    return [Rule(name, set(exts)) for name, exts in DEFAULT_CATEGORIES.items()]


def find_category(path: Path, rules: list[Rule]) -> str | None:
    # first matching rule wins, so custom rules can be put in front of the defaults
    for rule in rules:
        if rule.matches(path):
            return rule.category
    return None
