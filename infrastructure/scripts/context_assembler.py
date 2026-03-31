import sys
import json
import os
import subprocess
import argparse
import re

CONFIG_READER = os.path.join(os.path.dirname(__file__), "config_reader.py")

SOURCE_PATTERN = re.compile(r"Source:\s*\[\[(.*?)\]\]", re.IGNORECASE)


def get_config(section, key):
    result = subprocess.run(
        ["python3", CONFIG_READER, "-s", section, "-k", key],
        capture_output=True, text=True, check=True
    )
    return result.stdout.strip()


def main():
    parser = argparse.ArgumentParser(
        description="Assemble the context block for the final LLM call.")
    parser.add_argument("-Z", "--no-zettels", action="store_true", default=False,
                        dest="no_zettels", help="Exclude zettels from context")
    parser.add_argument("-W", "--no-wikis", action="store_true", default=False,
                        dest="no_wikis", help="Exclude wiki pages from context")
    parser.add_argument("-s", "--include-sources", action="store_true", default=False,
                        dest="include_sources",
                        help="Include original archived source documents")
    parser.add_argument("-m", "--metadata", type=json.loads, default={},
                        help="JSON dictionary of metadata (unused, required by convention)")
    args, _ = parser.parse_known_args()

    envelope = json.loads(sys.stdin.read())
    flags = envelope.get("flags", {})

    # Envelope flags take precedence over ritual-file flags (args).
    no_wikis        = flags.get("no_wikis",        args.no_wikis)
    no_zettels      = flags.get("no_zettels",      args.no_zettels)
    include_sources = flags.get("include_sources", args.include_sources)

    query          = envelope.get("query", "")
    ranked_zettels = envelope.get("ranked_zettels", [])
    wikis          = envelope.get("wikis", [])

    sections = []

    sections.append(f"## Query\n{query}")

    if not no_wikis and wikis:
        wiki_texts = "\n\n---\n\n".join(w["content"] for w in wikis)
        sections.append(f"## Relevant Wiki Pages\n{wiki_texts}")

    if not no_zettels and ranked_zettels:
        zettel_texts = "\n\n---\n\n".join(z["content"] for z in ranked_zettels)
        sections.append(f"## Relevant Notes\n{zettel_texts}")

    if include_sources and ranked_zettels:
        # Read path bases once, outside the loop.
        try:
            root_dir = get_config("spellbook", "root")
        except subprocess.CalledProcessError:
            root_dir = ""
        try:
            archive_dir = get_config("spellbook", "archive")
        except subprocess.CalledProcessError:
            archive_dir = ""

        source_texts = []
        for zettel in ranked_zettels:
            match = SOURCE_PATTERN.search(zettel["content"])
            if not match:
                continue
            source_ref = match.group(1).strip()
            # Try absolute, then CWD-relative (spellbook root), then archive-relative.
            candidates = [source_ref,
                          os.path.join(root_dir, source_ref) if root_dir else None,
                          os.path.join(archive_dir, source_ref) if archive_dir else None]
            source_path = next((p for p in candidates if p and os.path.exists(p)), None)
            if source_path is None:
                sys.stderr.write(f"Warning: source file not found on disk: {source_ref}\n")
                continue
            with open(source_path, "r", encoding="utf-8") as f:
                source_texts.append(f.read())
        if source_texts:
            sections.append("## Source Documents\n" + "\n\n---\n\n".join(source_texts))

    context = "\n\n".join(sections)

    if len(sections) == 1:
        sys.stderr.write(
            "Warning: no knowledge base content assembled for this query.\n"
        )

    envelope["context"] = context
    print(json.dumps(envelope))


if __name__ == "__main__":
    main()
