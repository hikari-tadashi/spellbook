import sys
import json
import os
import subprocess
import argparse

CONFIG_READER = os.path.join(os.path.dirname(__file__), "config_reader.py")


def get_config(section, key):
    result = subprocess.run(
        ["python3", CONFIG_READER, "-s", section, "-k", key],
        capture_output=True, text=True, check=True
    )
    return result.stdout.strip()


def main():
    parser = argparse.ArgumentParser(
        description="Load wiki pages for each matched tag.")
    parser.add_argument("-m", "--metadata", type=json.loads, default={},
                        help="JSON dictionary of metadata (unused, required by convention)")
    args, _ = parser.parse_known_args()

    envelope = json.loads(sys.stdin.read())
    tags = envelope.get("tags", [])

    try:
        wiki_dir = get_config("spellbook", "wiki")
    except subprocess.CalledProcessError:
        sys.stderr.write("Error: cannot read wiki directory from config.\n")
        sys.exit(1)

    if not os.path.isdir(wiki_dir):
        sys.stderr.write(
            f"Error: wiki directory not found at {wiki_dir}.\n"
            "Run 'spellbook wiki' first to generate wiki pages.\n"
        )
        sys.exit(1)

    wikis = []
    for tag in tags:
        wiki_path = os.path.join(wiki_dir, f"{tag}.md")
        if os.path.exists(wiki_path):
            with open(wiki_path, "r", encoding="utf-8") as f:
                content = f.read()
            wikis.append({
                "tag":     tag,
                "path":    wiki_path,
                "content": content,
            })

    envelope["wikis"] = wikis
    print(json.dumps(envelope))


if __name__ == "__main__":
    main()
