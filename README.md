# file-watchdog

A command line tool I made to clean up my Downloads folder.

It moves files into folders based on their type (Images, Documents, Videos and so on). It can also keep running in the background and sort new downloads as they come in, and it can find duplicate files.

![tests](https://github.com/bhargavithoka-overclocked/file-watchdog/actions/workflows/tests.yml/badge.svg)

## What it does

- Sorts files into folders by type
- Watches a folder and sorts new files automatically
- Finds duplicate files, even if they have different names
- Undo, in case you don't like the result
- Dry run, to see what would happen first
- Never overwrites a file. If `photo.jpg` already exists, the new one is saved as `photo (1).jpg`

## Setup

You need Python 3.11 or newer.

```bash
git clone https://github.com/bhargavithoka-overclocked/file-watchdog.git
cd file-watchdog
pip install .
```

## How to use it

Sort a folder:

```bash
file-watchdog sort ~/Downloads
```

Not sure? Add `--dry-run` to see what would move without changing anything:

```bash
file-watchdog sort ~/Downloads --dry-run
```

```
would move IMG_2041.jpg -> Images/
would move budget.xlsx -> Spreadsheets/
would move lecture-3.mp4 -> Videos/
would move resume_final.pdf -> Documents/
would move setup.dmg -> Installers/
```

Undo the last sort:

```bash
file-watchdog undo ~/Downloads
```

Keep it running so new downloads get sorted automatically (stop with Ctrl+C):

```bash
file-watchdog watch ~/Downloads
```

It waits until a download is finished before moving it, so half-downloaded files are left alone.

Find duplicate files:

```bash
file-watchdog dupes ~/Pictures
```

Add `--move` to move the extra copies into a `_duplicates` folder. Nothing gets deleted, so you can check them first.

Other options:

- `--by-date` puts files in year/month folders, like `Images/2026/11/`
- Files it doesn't recognise, folders, and hidden files are never touched

## Custom settings

You can add your own categories by putting a `file-watchdog.toml` file in the folder:

```toml
ignore = ["*.torrent"]

[categories]
Books = [".epub", ".mobi"]
Papers = [".pdf"]
```

Your categories are checked first, so in this example PDFs go into `Papers` instead of `Documents`. There's a longer example in [`examples/file-watchdog.toml`](examples/file-watchdog.toml).

## How it works

- `rules.py` has the list of file types
- `organizer.py` figures out where each file should go and moves it
- `journal.py` saves a record of every move so `undo` can put things back
- `dupes.py` finds duplicates. It first groups files by size (two files can't be the same if their sizes are different), then compares the SHA-256 hash only for files with the same size. This way most files never need to be read.
- `watcher.py` handles watch mode, using the [watchdog](https://pypi.org/project/watchdog/) library
- `cli.py` has the commands, built with [Typer](https://typer.tiangolo.com/) and [Rich](https://github.com/Textualize/rich)

## Running the tests

```bash
pip install -e ".[dev]"
pytest
```

## Things I might add later

- Sorting by file name too, e.g. put all `Screenshot*` files in a Screenshots folder
- Running watch mode automatically when my laptop starts

Made by Bhargavi Thoka
