import os
import sys
import re
import json
import shutil
import subprocess
import argparse
from datetime import datetime

MODEL = "cogito:8b"
OLLAMA_CALL = os.path.join(os.path.dirname(__file__), "ollama_call.py")
CONFIG_READER = os.path.join(os.path.dirname(__file__), "config_reader.py")

MAX_RETRIES = 3

def get_config(section, key):
    result = subprocess.run(
        ["python3", CONFIG_READER, "-s", section, "-k", key],
        capture_output=True, text=True, check=True
    )
    return result.stdout.strip()

try:
    MODEL = get_config("spellbook", "ollama_model")
except subprocess.CalledProcessError:
    pass

def parse_args():
    parser = argparse.ArgumentParser(description="Breaks text into atomic Zettelkasten notes using an LLM.")
    # Added a positional argument for the file to make it more robust
    parser.add_argument("file", nargs="?", help="Path to the file to process.")
    # metadata is required by spellbook script convention even if unused in this script.
    parser.add_argument("-m", "--metadata", type=json.loads, default={},
                        help="JSON dictionary of metadata to pass to the script.")
    return parser.parse_args()

def strip_markdown_fences(text):
    # LLMs commonly wrap JSON output in markdown code fences (```json ... ```) even
    # when instructed not to. Strip them before parsing to avoid spurious failures.
    text = text.strip()
    match = re.match(r'^```(?:json)?\s*([\s\S]*?)\s*```$', text)
    if match:
        return match.group(1)
    return text

def get_zettel_json(content):
    try:
        result = subprocess.run(
            ["python3", OLLAMA_CALL, "-m", MODEL, "-f", "json",
             "-s", "Break the following text into atomic Zettelkasten notes. Return ONLY a raw JSON list of strings, where each string is the content of an individual note. Do not include titles or keys. No markdown formatting, no explanations.",
             "-u", content],
            capture_output=True, text=True, check=True
        )
        return result.stdout
    except subprocess.CalledProcessError as e:
        sys.stderr.write(f"LLM Call Error: {e.stderr}\n")
        sys.exit(1)

def flatten_llm_output(data):
    flat_list = []
    if isinstance(data, list):
        for item in data:
            flat_list.extend(flatten_llm_output(item))
    elif isinstance(data, dict):
        for value in data.values():
            flat_list.extend(flatten_llm_output(value))
    elif isinstance(data, str):
        if data.strip():
            flat_list.append(data.strip())
    return flat_list

def main():
    args = parse_args()

    # Read filename from argument or stdin
    filepath = args.file
    if not filepath:
        if not sys.stdin.isatty():
            filepath = sys.stdin.read().strip()
        else:
            sys.stderr.write("Error: No file path provided.\n")
            sys.exit(1)

    archive_dir = get_config("spellbook", "archive")

    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            text_content = f.read()
    except Exception as e:
        sys.stderr.write(f"File Error: {e}\n")
        sys.exit(1)

    # Retry LLM call up to MAX_RETRIES times if JSON parsing fails.
    # strip_markdown_fences handles the most common formatting mistake before each attempt.
    zettel_data = None
    for attempt in range(1, MAX_RETRIES + 1):
        zettel_json = get_zettel_json(text_content)
        cleaned = strip_markdown_fences(zettel_json)
        try:
            raw_data = json.loads(cleaned)
            zettel_data = flatten_llm_output(raw_data)
            break
        except json.JSONDecodeError:
            sys.stderr.write(f"Warning: LLM output was not valid JSON (attempt {attempt}/{MAX_RETRIES}).\n")
            if attempt == MAX_RETRIES:
                sys.stderr.write("Error: All retry attempts exhausted. No notes created.\n")
                print(json.dumps([]))
                sys.exit(0)

    if not zettel_data:
        sys.stderr.write("Error: LLM returned empty data.\n")
        print("[]")
        sys.exit(0)

    filename = os.path.basename(filepath)
    archived_path = os.path.join(archive_dir, filename)
    source_link = f"Source: [[{archived_path}]]"

    for i in range(len(zettel_data)):
        zettel_data[i] = f"{zettel_data[i]}\n\n{source_link}"

    print(json.dumps(zettel_data, indent=2))

    # Archive only after successful LLM processing.
    # If a file with the same name already exists in the archive, append a timestamp
    # to the filename rather than overwriting or failing.
    try:
        if os.path.exists(archived_path):
            ts = datetime.now().strftime("%Y%m%d%H%M%S")
            name, ext = os.path.splitext(filename)
            archived_path = os.path.join(archive_dir, f"{name}-{ts}{ext}")
        shutil.move(filepath, archived_path)
    except Exception as e:
        sys.stderr.write(f"Archive Error: {e}\n")
        sys.exit(1)

if __name__ == "__main__":
    main()
