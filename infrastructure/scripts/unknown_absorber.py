#!/usr/bin/env python3
"""
unknown_absorber.py — Graceful fallback for unsupported file types.

Reads a file path from stdin.
Categorises the file by extension as media or data.
Moves it to assets/media/ or assets/data/ under the spellbook root.
Generates a brief zettel via the Oracle noting the file's arrival and location.
Outputs a JSON list (same format as zettelkasten_llm.py) so the downstream
pipeline (zettel_id_generator, tagger_llm) continues normally.

Called by dispatch.py when a file's extension is not in the known text set
and no plugin handler has claimed it.
"""

import os
import sys
import json
import shutil
import subprocess
from datetime import datetime

SCRIPT_DIR    = os.path.dirname(os.path.abspath(__file__))
CONFIG_READER = os.path.join(SCRIPT_DIR, "config_reader.py")
ORACLE_CALL   = os.path.join(SCRIPT_DIR, "oracle_call.py")

MEDIA_EXTENSIONS = {
    ".mp3", ".mp4", ".wav", ".flac", ".ogg", ".aac", ".m4a",
    ".avi", ".mov", ".mkv", ".wmv", ".webm",
    ".jpg", ".jpeg", ".png", ".gif", ".bmp", ".tiff", ".webp", ".heic", ".svg",
}


def get_config(section, key):
    result = subprocess.run(
        ["python3", CONFIG_READER, "-s", section, "-k", key],
        capture_output=True, text=True, check=True
    )
    return result.stdout.strip()


def main():
    file_path = sys.stdin.read().strip()
    if not file_path or not os.path.isfile(file_path):
        sys.stderr.write(f"unknown_absorber.py: not a valid file: '{file_path}'\n")
        sys.exit(1)

    fname    = os.path.basename(file_path)
    ext      = os.path.splitext(fname)[1].lower()
    category = "media" if ext in MEDIA_EXTENSIONS else "data"

    try:
        root = get_config("spellbook", "root")
    except subprocess.CalledProcessError:
        sys.stderr.write("unknown_absorber.py: could not read spellbook root from config.\n")
        sys.exit(1)

    try:
        model = get_config("spellbook", "oracle_model")
    except subprocess.CalledProcessError:
        model = "granite4:3b"

    assets_dir = os.path.join(root, "assets", category)
    os.makedirs(assets_dir, exist_ok=True)

    dest = os.path.join(assets_dir, fname)
    if os.path.exists(dest):
        ts        = datetime.now().strftime("%Y%m%d%H%M%S")
        name, raw_ext = os.path.splitext(fname)
        dest      = os.path.join(assets_dir, f"{name}-{ts}{raw_ext}")

    shutil.move(file_path, dest)
    rel_dest  = os.path.relpath(dest)
    ext_label = ext if ext else "(no extension)"

    system_prompt = (
        "You are recording the arrival of a file that cannot be automatically processed as text. "
        "Write a single short Zettelkasten note (2-4 sentences) noting: the file's name, "
        "its apparent type based on the extension, and where it has been filed. "
        "Note that it may require manual processing or a plugin to handle. "
        "Do not invent information. Do not use headings. Write in plain prose."
    )
    user_prompt = (
        f"File name: {fname}\n"
        f"File type: {ext_label}\n"
        f"Filed at: {rel_dest}"
    )

    try:
        result = subprocess.run(
            ["python3", ORACLE_CALL, "-m", model, "-s", system_prompt, "-u", user_prompt],
            capture_output=True, text=True, check=True
        )
        zettel_text = result.stdout.strip()
    except subprocess.CalledProcessError as e:
        # Oracle unavailable — write a minimal zettel without LLM so the pipeline
        # still completes and the file is at least recorded.
        zettel_text = (
            f"A file named '{fname}' ({ext_label}) was received in the inbox and could not "
            f"be processed automatically. It has been filed at {rel_dest} and may require "
            f"manual processing or a plugin handler."
        )
        sys.stderr.write(
            f"unknown_absorber.py: Oracle call failed, using fallback zettel. {e.stderr.strip()}\n"
        )

    print(json.dumps([f"{zettel_text}\n\nSource: [[{rel_dest}]]"]))
    sys.stderr.write(f"unknown_absorber.py: filed '{fname}' → '{dest}'\n")


if __name__ == "__main__":
    main()
