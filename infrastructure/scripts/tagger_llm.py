import sys
import json
import os
import subprocess
import argparse
from datetime import datetime, timedelta

# cogito:8b seems to follow the rules better then Llama3.1:8b
# trying out granite, lets see how IBM does
MODEL = "granite4:3b"
HOST  = "http://localhost:11434"
ORACLE_CALL = os.path.join(os.path.dirname(__file__), "oracle_call.py")
CONFIG_READER = os.path.join(os.path.dirname(__file__), "config_reader.py")

MAX_RETRIES = 3

def get_config(section, key):
    result = subprocess.run(
        ["python3", CONFIG_READER, "-s", section, "-k", key],
        capture_output=True, text=True, check=True
    )
    return result.stdout.strip()

def get_canonical_tags():
    result = subprocess.run(
        ["python3", CONFIG_READER, "-s", "tags", "--list-keys"],
        capture_output=True, text=True, check=True
    )
    return [line.strip() for line in result.stdout.splitlines() if line.strip()]

try:
    MODEL = get_config("spellbook", "tagger_model")
except subprocess.CalledProcessError:
    try:
        MODEL = get_config("spellbook", "oracle_model")
    except subprocess.CalledProcessError:
        pass

try:
    _host = get_config("spellbook", "oracle_host")
    HOST = _host if _host.startswith("http") else f"http://{_host}"
except subprocess.CalledProcessError:
    pass

try:
    ALLOWED_TAGS = ", ".join(get_canonical_tags())
except subprocess.CalledProcessError:
    ALLOWED_TAGS = "todo, inbox, reference, archive, journal, people, events, health, finances, home, travel, work, projects, meetings, decisions, goals, learning, book, article, course, idea, question, science, technology, history, philosophy, economics, politics, culture, art, language, writing, music, design"

def parse_args():
    parser = argparse.ArgumentParser(description="Tags notes using an LLM.")
    parser.add_argument("-m", "--metadata", type=json.loads, default={},
                        help="JSON dictionary of metadata to pass to the script.")
    return parser.parse_args()

def get_tags(content):
    # Tags are passed through as-is from the LLM without strict validation.
    # Drift from ALLOWED_TAGS (extra tags, varied phrasing) is intentional:
    # the garden process downstream is responsible for normalising and curating tags.
    try:
        result = subprocess.run(
            ["python3", ORACLE_CALL, "-m", MODEL, "-H", HOST,
             "-s", f"Select tags strictly from this list: [{ALLOWED_TAGS}]. Avoid 'other' unless necessary. Use tags moderately. Return ONLY the selected tags formatted with hash signs (e.g. #science #logic).",
             "-u", content],
            capture_output=True, text=True, check=True
        )
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        sys.stderr.write(f"Tagging Error: {e.stderr}\n")
        return "#other"

def write_note(notes_dir, title, final_content):
    """Write a note, handling filename collisions by reassigning timestamps to both files.

    When a collision occurs the existing file and the new note each receive a fresh
    timestamp filename and a #collision-{original_timestamp} tag so the garden process
    can identify and reconcile them. Retried up to MAX_RETRIES times in case the
    freshly generated timestamps also collide (unlikely but possible under rapid runs).
    """
    file_path = os.path.join(notes_dir, f"{title}.md")

    for attempt in range(MAX_RETRIES + 1):
        if not os.path.exists(file_path):
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(final_content)
            return file_path

        if attempt == MAX_RETRIES:
            sys.stderr.write(f"Error: Could not resolve collision after {MAX_RETRIES} retries for {title}.\n")
            return None

        # Collision: strip both notes' old timestamp filenames, assign new ones,
        # and tag both with the colliding timestamp so they can be found later.
        collision_tag = f"#collision-{title}"

        with open(file_path, "r", encoding="utf-8") as f:
            existing_content = f.read()

        now = datetime.now()
        new_ts_existing = now.strftime("%Y%m%d%H%M%S")
        new_ts_new = (now + timedelta(seconds=1)).strftime("%Y%m%d%H%M%S")

        new_existing_path = os.path.join(notes_dir, f"{new_ts_existing}.md")
        with open(new_existing_path, "w", encoding="utf-8") as f:
            f.write(f"{existing_content}\n{collision_tag}")
        os.remove(file_path)

        title = new_ts_new
        file_path = os.path.join(notes_dir, f"{new_ts_new}.md")
        final_content = f"{final_content}\n{collision_tag}"

        sys.stderr.write(
            f"Collision (attempt {attempt + 1}): relocated existing note to {new_ts_existing}, "
            f"retrying new note as {new_ts_new}.\n"
        )

def main():
    args = parse_args()
    metadata = args.metadata  # Unused here but required by spellbook script convention.

    NOTES_DIR = get_config("spellbook", "notes")

    # Ensure notes directory exists
    os.makedirs(NOTES_DIR, exist_ok=True)

    # Read JSON input from pipe
    try:
        input_data = sys.stdin.read()
        zettels = json.loads(input_data)
    except json.JSONDecodeError:
        sys.stderr.write("Error: Invalid JSON input.\n")
        sys.exit(1)

    # Iterate, Tag, and Save
    for title, content in zettels.items():
        tags = get_tags(content)
        final_content = f"{content}\n\n{tags}"

        # Sanitize filename
        safe_title = "".join([c for c in title if c.isalpha() or c.isdigit() or c == ' ']).rstrip()

        saved_path = write_note(NOTES_DIR, safe_title, final_content)
        if saved_path:
            print(f"Saved: {saved_path}")

if __name__ == "__main__":
    main()
