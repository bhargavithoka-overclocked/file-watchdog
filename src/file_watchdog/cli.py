from collections import Counter
from pathlib import Path
from typing import Annotated

import typer
from rich.console import Console
from rich.table import Table

from .config import ConfigError, find_config, load_config
from .journal import Journal
from .organizer import Move, Organizer

app = typer.Typer(
    help="Keep your folders tidy by sorting files into folders by type.",
    no_args_is_help=True,
    add_completion=False,
)
console = Console()


@app.callback()
def main():
    pass


ConfigOption = Annotated[
    Path | None,
    typer.Option("--config", "-c", exists=True, dir_okay=False, help="Path to a file-watchdog.toml file."),
]


def build_organizer(folder: Path, config_path: Path | None, by_date: bool = False) -> Organizer:
    config_path = config_path or find_config(folder)
    try:
        config = load_config(config_path)
    except ConfigError as e:
        console.print(f"[red]Config error:[/] {e}")
        raise typer.Exit(1)
    if config_path:
        console.print(f"[dim]Using config {config_path}[/]")
    return Organizer(
        folder,
        rules=config.rules,
        ignore=config.ignore,
        date_folders=by_date or config.date_folders,
    )


def print_summary(moves: list[Move], title: str):
    counts = Counter(move.category for move in moves)
    table = Table(title=title)
    table.add_column("Category")
    table.add_column("Files", justify="right")
    for category, count in sorted(counts.items()):
        table.add_row(category, str(count))
    console.print(table)


@app.command()
def sort(
    folder: Annotated[Path, typer.Argument(exists=True, file_okay=False, help="Folder to sort.")],
    dry_run: Annotated[bool, typer.Option("--dry-run", "-n", help="Show what would move without moving anything.")] = False,
    by_date: Annotated[bool, typer.Option("--by-date", help="Put files in year/month subfolders, e.g. Images/2026/11.")] = False,
    config: ConfigOption = None,
):
    """Sort the files in FOLDER into category folders."""
    organizer = build_organizer(folder, config, by_date)
    moves = organizer.plan()

    if not moves:
        console.print("Nothing to sort here.")
        return

    if dry_run:
        for move in moves:
            target = move.destination.parent.relative_to(organizer.root)
            console.print(f"[dim]would move[/] {move.source.name} [cyan]-> {target}/[/]")
        print_summary(moves, "Dry run")
        return

    moves = organizer.apply(moves)
    Journal(organizer.root).record(moves)
    for move in moves:
        console.print(f"{move.source.name} [cyan]-> {move.destination.relative_to(organizer.root)}[/]")
    print_summary(moves, f"Moved {len(moves)} file(s)")
    console.print("[dim]Changed your mind? Run [bold]file-watchdog undo[/bold] on the same folder.[/]")


@app.command()
def undo(
    folder: Annotated[Path, typer.Argument(exists=True, file_okay=False, help="Folder that was sorted.")],
):
    """Put back the files moved by the last run in FOLDER."""
    journal = Journal(folder.expanduser().resolve())
    result = journal.undo_last()
    if result is None:
        console.print("Nothing to undo.")
        return

    for problem in result.problems:
        console.print(f"[yellow]warning:[/] {problem}")
    console.print(f"Restored {result.restored} file(s).")
