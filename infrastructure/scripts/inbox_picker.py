import os
import random
import sys
import argparse
import json
import subprocess

CONFIG_READER = os.path.join(os.path.dirname(__file__), "config_reader.py")
EXTENSIONS = {".md", ".txt"}

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

    # Filter files
    files = [
        f for f in os.listdir(INBOX_DIR) 
        if os.path.isfile(os.path.join(INBOX_DIR, f)) 
        and os.path.splitext(f)[1].lower() in EXTENSIONS
    ]

    if not files:
        sys.stderr.write("Error: No markdown or text files in inbox.\n")
        sys.exit(1)

    # Pick random file and print absolute path to stdout
    selected_file = os.path.join(INBOX_DIR, random.choice(files))
    print(selected_file)

if __name__ == "__main__":
    main()