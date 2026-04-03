import os
import random
import sys
import argparse
import json
import subprocess

CONFIG_READER = os.path.join(os.path.dirname(__file__), "config_reader.py")

def get_config(section, key):
    result = subprocess.run(
        ["python3", CONFIG_READER, "-s", section, "-k", key],
        capture_output=True, text=True, check=True
    )
    return result.stdout.strip()

def parse_args():
    parser = argparse.ArgumentParser(description="Picks a random markdown or text file from the inbox.")
    # metadata is required by spellbook script convention even if unused in this script.
    parser.add_argument("-m", "--metadata", type=json.loads, default={},
                        help="JSON dictionary of metadata to pass to the script.")
    return parser.parse_args()

def main():
    args = parse_args()
    metadata = args.metadata  # Unused here but required by spellbook script convention.

    INBOX_DIR = get_config("spellbook", "inbox")

    # Ensure inbox exists
    if not os.path.exists(INBOX_DIR):
        sys.stderr.write(f"Error: Directory '{INBOX_DIR}' not found.\n")
        sys.exit(1)

    candidates = [
        os.path.join(INBOX_DIR, f)
        for f in os.listdir(INBOX_DIR)
        if not f.startswith(".")  # skip hidden files and .DS_Store etc.
    ]

    if not candidates:
        sys.stderr.write("Error: No files or folders in inbox.\n")
        sys.exit(1)

    selected = random.choice(candidates)
    remaining = len(candidates) - 1
    sys.stderr.write(f"[absorb] Processing: {os.path.basename(selected)} ({remaining} remaining in inbox)\n")
    print(selected)

if __name__ == "__main__":
    main()