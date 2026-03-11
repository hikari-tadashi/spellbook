#!/usr/bin/env python3
"""
reset.py — Moves archived content back to inbox and wipes processed notes/maps.
WARNING: destructive. Useful for a clean re-ingest of everything.

Reads paths from spellbook.conf via config_reader.py so this script can be
run from any directory as long as spellbook.conf is findable upstream.
"""

import sys
import shutil
import subprocess
from pathlib import Path

SCRIPT_DIR = Path(__file__).parent


def get_config(key):
    result = subprocess.run(
        [sys.executable, str(SCRIPT_DIR / "config_reader.py"), "-s", "spellbook", "-k", key],
        capture_output=True,
        text=True,
        check=True,
    )
    return Path(result.stdout.strip())


def main():
    inbox = get_config("inbox")
    archive = get_config("archive")
    notes = get_config("notes")
    maps = get_config("maps")

    print(f"inbox:   {inbox}")
    print(f"archive: {archive}")
    print(f"notes:   {notes}")
    print(f"maps:    {maps}")

    if archive.exists():
        for item in archive.iterdir():
            shutil.move(str(item), inbox / item.name)
    else:
        print(f"warning: archive directory not found, skipping: {archive}")

    if notes.exists():
        for item in notes.iterdir():
            shutil.rmtree(item) if item.is_dir() else item.unlink()
    else:
        print(f"warning: notes directory not found, skipping: {notes}")

    if maps.exists():
        for item in maps.iterdir():
            shutil.rmtree(item) if item.is_dir() else item.unlink()
    else:
        print(f"warning: maps directory not found, skipping: {maps}")


if __name__ == "__main__":
    main()
