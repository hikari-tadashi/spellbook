import sys
import json
import os
import subprocess
import argparse
import re

MODEL = "granite4:3b"
HOST  = "http://localhost:11434"
ORACLE_CALL   = os.path.join(os.path.dirname(__file__), "oracle_call.py")
CONFIG_READER = os.path.join(os.path.dirname(__file__), "config_reader.py")


def get_config(section, key):
    result = subprocess.run(
        ["python3", CONFIG_READER, "-s", section, "-k", key],
        capture_output=True, text=True, check=True
    )
    return result.stdout.strip()


# Model resolution: query_tagger_model > query_model > ollama_model > script default.
try:
    MODEL = get_config("spellbook", "query_tagger_model")
except subprocess.CalledProcessError:
    try:
        MODEL = get_config("spellbook", "query_model")
    except subprocess.CalledProcessError:
        try:
            MODEL = get_config("spellbook", "ollama_model")
        except subprocess.CalledProcessError:
            pass

try:
    _host = get_config("spellbook", "ollama_host")
    HOST = _host if _host.startswith("http") else f"http://{_host}"
except subprocess.CalledProcessError:
    pass


def main():
    parser = argparse.ArgumentParser(
        description="Tag the query using canonical tags from the knowledge base.")
    parser.add_argument("-m", "--metadata", type=json.loads, default={},
                        help="JSON dictionary of metadata (unused, required by convention)")
    args, _ = parser.parse_known_args()

    envelope = json.loads(sys.stdin.read())
    query = envelope["query"]

    try:
        taghub = get_config("spellbook", "taghub")
    except subprocess.CalledProcessError:
        sys.stderr.write("Error: cannot read taghub from config.\n")
        sys.exit(1)

    canon_file = os.path.join(taghub, "canon-tags")
    if not os.path.exists(canon_file):
        sys.stderr.write(
            f"Error: canon-tags not found at {canon_file}.\n"
            "Run the focus ritual first to build the tag index.\n"
        )
        sys.exit(1)

    with open(canon_file, "r", encoding="utf-8") as f:
        canon_tags = [line.strip() for line in f if line.strip()]
    canon_set = set(canon_tags)

    system_prompt = (
        "You are a tag selector for a personal knowledge base.\n"
        "Given a question and a list of canonical tags, select only the tags\n"
        "that are directly relevant to answering the question.\n"
        "Return ONLY the selected tag names, space-separated, with no punctuation,\n"
        "no explanations, and no hash symbols. If no tags are relevant, return\n"
        "the single word: none"
    )

    user_prompt = (
        f"Question: {query}\n\n"
        "Canonical tags (select from these only):\n"
        + "\n".join(canon_tags)
        + "\n\nReturn only the relevant tag names, space-separated."
    )

    try:
        result = subprocess.run(
            ["python3", ORACLE_CALL, "-m", MODEL, "-H", HOST,
             "-s", system_prompt, "-u", user_prompt],
            capture_output=True, text=True, check=True
        )
        response = result.stdout.strip()
    except subprocess.CalledProcessError as e:
        sys.stderr.write(f"Warning: LLM call failed: {e.stderr}\n")
        envelope["tags"] = []
        print(json.dumps(envelope))
        return

    tags = []
    if response.strip().lower() != "none":
        for token in response.split():
            cleaned = re.sub(r"[^\w\-]", "", token)
            if cleaned and cleaned in canon_set:
                tags.append(cleaned)

    if not tags:
        sys.stderr.write(
            "Warning: no canonical tags matched for this query. Results may be limited.\n"
        )

    envelope["tags"] = tags
    print(json.dumps(envelope))


if __name__ == "__main__":
    main()
