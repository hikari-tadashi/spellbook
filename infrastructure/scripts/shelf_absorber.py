#!/usr/bin/env python3
"""
shelf_absorber.py — Shelves a folder and generates an anchor zettel.

Reads a folder path from stdin.
Moves the folder to content/shelves/{name}/.
Generates an anchor zettel via the Oracle.
Outputs a JSON list containing the anchor zettel text (same format as
zettelkasten_llm.py), so dispatch.py can forward it into the normal
zettel_id_generator | tagger_llm pipeline.
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

MAX_ROOT_FILE_CHARS = 4000  # max chars read from any single root-level text file
MAX_TREE_ENTRIES    = 200   # max lines in the file tree listing


def get_config(section, key):
    result = subprocess.run(
        ["python3", CONFIG_READER, "-s", section, "-k", key],
        capture_output=True, text=True, check=True
    )
    return result.stdout.strip()


def build_file_tree(folder_path, max_entries=MAX_TREE_ENTRIES):
    """Return a text listing of the folder's file tree, truncated if large."""
    lines = []
    for root, dirs, files in os.walk(folder_path):
        dirs[:] = [d for d in sorted(dirs) if not d.startswith(".")]
        depth  = root.replace(folder_path, "").count(os.sep)
        indent = "  " * depth
        lines.append(f"{indent}{os.path.basename(root)}/")
        for fname in sorted(files):
            if not fname.startswith("."):
                lines.append(f"{indent}  {fname}")
        if len(lines) >= max_entries:
            lines.append("  ... (truncated)")
            break
    return "\n".join(lines)


def collect_root_text(folder_path):
    """
    Read text content from markdown and text files at the root level only.
    Returns a combined string, truncated per file.
    """
    readable = {".md", ".txt", ".rst"}
    parts = []
    for fname in sorted(os.listdir(folder_path)):
        if fname.startswith("."):
            continue
        fpath = os.path.join(folder_path, fname)
        if os.path.isfile(fpath) and os.path.splitext(fname)[1].lower() in readable:
            try:
                with open(fpath, encoding="utf-8", errors="replace") as f:
                    content = f.read(MAX_ROOT_FILE_CHARS)
                parts.append(f"--- {fname} ---\n{content}")
            except Exception:
                pass
    return "\n\n".join(parts)


def main():
    folder_path = sys.stdin.read().strip()
    if not folder_path or not os.path.isdir(folder_path):
        sys.stderr.write(f"shelf_absorber.py: not a valid folder: '{folder_path}'\n")
        sys.exit(1)

    # Config
    try:
        shelves_dir = get_config("spellbook", "shelves")
    except subprocess.CalledProcessError:
        archive     = get_config("spellbook", "archive")
        shelves_dir = os.path.join(archive, "shelves")

    try:
        model = get_config("spellbook", "shelf_model")
    except subprocess.CalledProcessError:
        try:
            model = get_config("spellbook", "oracle_model")
        except subprocess.CalledProcessError:
            model = "qwen/qwen3.5-9b"

    os.makedirs(shelves_dir, exist_ok=True)

    # Resolve destination — handle name collisions with timestamp suffix
    folder_name = os.path.basename(folder_path.rstrip("/\\"))
    dest        = os.path.join(shelves_dir, folder_name)
    if os.path.exists(dest):
        ts   = datetime.now().strftime("%Y%m%d%H%M%S")
        dest = os.path.join(shelves_dir, f"{folder_name}-{ts}")

    # Collect content before moving
    file_tree = build_file_tree(folder_path)
    root_text = collect_root_text(folder_path)

    # Move folder to shelf
    shutil.move(folder_path, dest)
    rel_shelf_path = os.path.relpath(dest)

    # Assemble Oracle prompt
    user_prompt = f"Folder name: {folder_name}\n\nFile tree:\n{file_tree}\n"
    if root_text:
        user_prompt += f"\nRoot-level document content:\n{root_text}\n"

    system_prompt = (
        "You are summarising a folder that has been shelved in a personal knowledge base. "
        "Write a single concise Zettelkasten note (150-400 words) that describes: "
        "what this folder contains, its apparent purpose, and any key themes or topics. "
        "Do not use headings. Write in plain prose. "
        "Do not invent information not present in the file tree or documents provided."
    )

    try:
        result = subprocess.run(
            ["python3", ORACLE_CALL, "-m", model, "-s", system_prompt, "-u", user_prompt],
            capture_output=True, text=True, check=True
        )
        anchor_text = result.stdout.strip()
    except subprocess.CalledProcessError as e:
        sys.stderr.write(f"shelf_absorber.py: Oracle call failed: {e.stderr}\n")
        sys.exit(1)

    # Append source link and emit as a JSON list (same format as zettelkasten_llm.py)
    anchor_with_link = f"{anchor_text}\n\nSource: [[{rel_shelf_path}]]"
    print(json.dumps([anchor_with_link]))

    sys.stderr.write(f"shelf_absorber.py: shelved '{folder_name}' → '{dest}'\n")


if __name__ == "__main__":
    main()
