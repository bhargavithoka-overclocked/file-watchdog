from pathlib import Path
from typing import Annotated

import typer

from .organizer import Organizer

app = typer.Typer(
    help="Keep your folders tidy by sorting files into folders by type.",
    no_args_is_help=True,
    add_completion=False,
)


@app.callback()
def main():
    pass


@app.command()
def sort(
    folder: Annotated[Path, typer.Argument(exists=True, file_okay=False, help="Folder to sort.")],
):
    """Sort the files in FOLDER into category folders."""
    organizer = Organizer(folder)
    moves = organizer.apply(organizer.plan())

    for move in moves:
        typer.echo(f"{move.source.name} -> {move.category}/")
    typer.echo(f"Moved {len(moves)} file(s).")
