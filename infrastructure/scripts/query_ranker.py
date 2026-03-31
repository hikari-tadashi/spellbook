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
        description="Score and rank zettels by tag overlap with the query tags.")
    parser.add_argument("-m", "--metadata", type=json.loads, default={},
                        help="JSON dictionary of metadata (unused, required by convention)")
    args, _ = parser.parse_known_args()

    envelope = json.loads(sys.stdin.read())
    query_tags = set(envelope.get("tags", []))
    zettels    = envelope.get("zettels", [])

    try:
        max_results = int(get_config("spellbook", "query_max_results"))
    except Exception:
        max_results = 10

    # Score by tag overlap; tie-break by id descending (newer zettels preferred).
    scored = []
    for zettel in zettels:
        score = len(set(zettel.get("tags", [])) & query_tags)
        scored.append({**zettel, "score": score})

    scored.sort(key=lambda z: (z["score"], z["id"]), reverse=True)
    top = scored[:max_results]

    if top and top[0]["score"] == 0:
        sys.stderr.write(
            "Warning: no tag overlap found between query and knowledge base.\n"
            "The query may cover a topic not yet in your Spellbook.\n"
        )

    envelope["ranked_zettels"] = top
    print(json.dumps(envelope))


if __name__ == "__main__":
    main()
