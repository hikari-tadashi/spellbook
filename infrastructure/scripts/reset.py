#!/usr/bin/env python3
"""
reset.py — Moves archived content back to inbox and wipes processed notes/maps.
WARNING: destructive. Useful for a clean re-ingest of everything.

Reads paths from spellbook.conf via config_reader.py so this script can be
run from any directory as long as spellbook.conf is findable upstream.

Options:
    -d, --default   Create any missing directories defined in [spellbook] conf
                    before performing the standard reset.
"""

import sys
import os
import argparse
import configparser
import shutil
import subprocess
from pathlib import Path

SCRIPT_DIR = Path(__file__).parent


def find_config(start_dir):
    """Search upward from start_dir for spellbook.conf."""
    current = os.path.abspath(start_dir)
    while True:
        candidate = os.path.join(current, "spellbook.conf")
        if os.path.isfile(candidate):
            return candidate
        parent = os.path.dirname(current)
        if parent == current:
            break
        current = parent
    return None


def get_config(key):
    result = subprocess.run(
        [sys.executable, str(SCRIPT_DIR / "config_reader.py"), "-s", "spellbook", "-k", key],
        capture_output=True,
        text=True,
        check=True,
    )
    return Path(result.stdout.strip())


def ensure_default_dirs():
    """Create all path-valued directories in [spellbook] that don't yet exist."""
    config_path = find_config(str(SCRIPT_DIR))
    if not config_path:
        print("error: could not find spellbook.conf", file=sys.stderr)
        sys.exit(1)

    config = configparser.RawConfigParser(allow_no_value=True)
    config.optionxform = str
    config.read(config_path)
    config_dir = os.path.dirname(config_path)

    if not config.has_section("spellbook"):
        print("error: [spellbook] section not found in config", file=sys.stderr)
        sys.exit(1)

    for key, value in config.items("spellbook"):
        if not value:
            continue
        # Skip non-path values (hostnames, model names, etc.) before resolving
        if not (os.path.isabs(value) or value.startswith((".", "/", "\\"))):
            continue
        # Resolve relative paths the same way config_reader.py does
        if not os.path.isabs(value):
            value = os.path.normpath(os.path.join(config_dir, value))
        p = Path(value)
        if not p.exists():
            print(f"creating: {p}")
            p.mkdir(parents=True, exist_ok=True)
        else:
            print(f"exists:   {p}")


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument(
        "-d", "--default",
        action="store_true",
        help="Create missing directories from [spellbook] conf before resetting",
    )
    args = parser.parse_args()

    if args.default:
        print("--- ensuring default directories ---")
        ensure_default_dirs()
        print()

    inbox   = get_config("inbox")
    archive = get_config("archive")
    notes   = get_config("notes")
    maps    = get_config("maps")
    root    = get_config("root")

    try:
        shelves = get_config("shelves")
    except subprocess.CalledProcessError:
        shelves = root / "content" / "shelves"

    assets_media = root / "assets" / "media"
    assets_data  = root / "assets" / "data"

    print(f"inbox:        {inbox}")
    print(f"archive:      {archive}")
    print(f"shelves:      {shelves}")
    print(f"assets/media: {assets_media}")
    print(f"assets/data:  {assets_data}")
    print(f"notes:        {notes}")
    print(f"maps:         {maps}")

    # Move archived originals back to inbox
    if archive.exists():
        for item in archive.iterdir():
            shutil.move(str(item), inbox / item.name)
    else:
        print(f"warning: archive directory not found, skipping: {archive}")

    # Move shelved folders back to inbox
    if shelves.exists():
        for item in shelves.iterdir():
            shutil.move(str(item), inbox / item.name)
    else:
        print(f"warning: shelves directory not found, skipping: {shelves}")

    # Move filed assets back to inbox
    for assets_dir in (assets_media, assets_data):
        if assets_dir.exists():
            for item in assets_dir.iterdir():
                shutil.move(str(item), inbox / item.name)

    # Wipe processed output
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
