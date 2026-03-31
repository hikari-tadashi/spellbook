import sys
import json
import os
import subprocess
import argparse
import re

CONFIG_READER = os.path.join(os.path.dirname(__file__), "config_reader.py")

TAG_PATTERN = re.compile(r"(?:^|\s)#([\w\-]+)")


def get_config(section, key):
    result = subprocess.run(
        ["python3", CONFIG_READER, "-s", section, "-k", key],
        capture_output=True, text=True, check=True
    )
    return result.stdout.strip()


def main():
    parser = argparse.ArgumentParser(
        description="Collect all zettels associated with any matched tag.")
    parser.add_argument("-m", "--metadata", type=json.loads, default={},
                        help="JSON dictionary of metadata (unused, required by convention)")
    args, _ = parser.parse_known_args()

    envelope = json.loads(sys.stdin.read())
    tags = envelope.get("tags", [])

    try:
        taghub_dir = get_config("spellbook", "taghub")
    except subprocess.CalledProcessError:
        sys.stderr.write("Error: cannot read taghub from config.\n")
        sys.exit(1)

    try:
        notes_dir = get_config("spellbook", "notes")
    except subprocess.CalledProcessError:
        sys.stderr.write("Error: cannot read notes directory from config.\n")
        sys.exit(1)

    if not os.path.isdir(notes_dir):
        sys.stderr.write(f"Error: notes directory not found at {notes_dir}.\n")
        sys.exit(1)

    # Collect union of zettel filenames across all matched tags.
    filenames_seen = set()
    for tag in tags:
        hub_file = os.path.join(taghub_dir, f"tag-hub-{tag}")
        if not os.path.exists(hub_file):
            continue
        with open(hub_file, "r", encoding="utf-8") as f:
            for line in f:
                fname = line.strip()
                if fname:
                    filenames_seen.add(fname)

    zettels = []
    for fname in sorted(filenames_seen):
        note_path = os.path.join(notes_dir, fname)
        if not os.path.exists(note_path):
            sys.stderr.write(f"Warning: zettel listed in tag-hub not found on disk: {note_path}\n")
            continue
        with open(note_path, "r", encoding="utf-8") as f:
            content = f.read()
        note_tags = TAG_PATTERN.findall(content)
        zettel_id = fname[:-3] if fname.endswith(".md") else fname
        zettels.append({
            "id":      zettel_id,
            "path":    note_path,
            "content": content,
            "tags":    note_tags,
            "score":   0,
        })

    envelope["zettels"] = zettels
    print(json.dumps(envelope))


if __name__ == "__main__":
    main()
