from collections import Counter
from pathlib import Path
from typing import Annotated

import typer
from rich.console import Console
from rich.table import Table

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
):
    """Sort the files in FOLDER into category folders."""
    organizer = Organizer(folder)
    moves = organizer.plan()

    if not moves:
        console.print("Nothing to sort here.")
        return

    if dry_run:
        for move in moves:
            console.print(f"[dim]would move[/] {move.source.name} [cyan]-> {move.category}/[/]")
        print_summary(moves, "Dry run")
        return

    moves = organizer.apply(moves)
    for move in moves:
        console.print(f"{move.source.name} [cyan]-> {move.destination.relative_to(organizer.root)}[/]")
    print_summary(moves, f"Moved {len(moves)} file(s)")
