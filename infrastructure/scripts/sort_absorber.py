#!/usr/bin/env python3
"""
sort_absorber.py — Files a processed asset to its destination.

Reads a JSON object from stdin:
  {
    "file":        "/path/to/file",          (required)
    "destination": "/path/to/dest/dir/",     (required)
    "backlink":    "/path/to/backlink/file"  (optional)
  }

Moves the file to destination/. Writes a backlink record if requested.
This is the plugin landing point for typed file absorption.
"""

import os
import sys
import json
import shutil
from datetime import datetime


def main():
    raw = sys.stdin.read().strip()
    if not raw:
        sys.stderr.write("sort_absorber.py: no input received.\n")
        sys.exit(1)

    try:
        payload = json.loads(raw)
    except json.JSONDecodeError:
        sys.stderr.write("sort_absorber.py: invalid JSON on stdin.\n")
        sys.exit(1)

    file_path   = payload.get("file", "").strip()
    destination = payload.get("destination", "").strip()
    backlink    = payload.get("backlink", "").strip()

    if not file_path or not os.path.isfile(file_path):
        sys.stderr.write(f"sort_absorber.py: file not found: '{file_path}'\n")
        sys.exit(1)

    if not destination:
        sys.stderr.write("sort_absorber.py: no destination specified.\n")
        sys.exit(1)

    os.makedirs(destination, exist_ok=True)

    fname = os.path.basename(file_path)
    dest  = os.path.join(destination, fname)

    # Collision handling — timestamp suffix
    if os.path.exists(dest):
        ts        = datetime.now().strftime("%Y%m%d%H%M%S")
        name, ext = os.path.splitext(fname)
        dest      = os.path.join(destination, f"{name}-{ts}{ext}")

    shutil.move(file_path, dest)

    if backlink:
        os.makedirs(os.path.dirname(backlink), exist_ok=True)
        with open(backlink, "a", encoding="utf-8") as f:
            f.write(f"- [[{dest}]]\n")

    sys.stderr.write(f"sort_absorber.py: filed '{fname}' → '{dest}'\n")


if __name__ == "__main__":
    main()
