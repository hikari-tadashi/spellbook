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


def str_to_bool(s):
    return s.strip().lower() in ("true", "1", "yes")


def make_parser():
    parser = argparse.ArgumentParser(
        description="Parse query and flags for the Spellbook query pipeline.",
        epilog=(
            "This is a natural language search, not a database query.\n"
            "Ask questions the way you would ask a person, not a search engine.\n"
            "\n"
            "Examples:\n"
            "  spellbook query what is the Zettelkasten method\n"
            '  spellbook query "what do I know about philosophy?"\n'
            "  spellbook query --no-wikis what did I write about Mersault\n"
            '  echo "what is stoicism?" | spellbook query\n'
            "  spellbook query          (launches interactive prompt)"
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("-W", "--no-wikis", action="store_true", default=None,
                        dest="no_wikis", help="Exclude wiki pages from context")
    parser.add_argument("-Z", "--no-zettels", action="store_true", default=None,
                        dest="no_zettels", help="Exclude zettels from context")
    parser.add_argument("-s", "--include-sources", action="store_true", default=None,
                        dest="include_sources",
                        help="Include original archived source documents")
    parser.add_argument("-o", "--mode", default=None,
                        choices=["prose", "cited", "json"],
                        help="Output mode: prose, cited, or json")
    parser.add_argument("-m", "--metadata", type=json.loads, default={},
                        help="JSON dictionary of metadata (unused, required by convention)")
    return parser


def merge_flags(args, inner_args):
    """Copy flags from inner_args into args only when args doesn't already have them."""
    if args.no_wikis is None and inner_args.no_wikis:
        args.no_wikis = True
    if args.no_zettels is None and inner_args.no_zettels:
        args.no_zettels = True
    if args.include_sources is None and inner_args.include_sources:
        args.include_sources = True
    if args.mode is None and inner_args.mode is not None:
        args.mode = inner_args.mode


def main():
    # Load conf defaults for each flag.
    conf_defaults = {}
    for conf_key, flag_key, hardcoded in [
        ("no-wikis",        "no_wikis",        False),
        ("no-zettels",      "no_zettels",      False),
        ("include-sources", "include_sources", False),
        ("mode",            "mode",            "prose"),
    ]:
        try:
            val = get_config("query-args-handler", conf_key)
            conf_defaults[flag_key] = val if flag_key == "mode" else str_to_bool(val)
        except subprocess.CalledProcessError:
            conf_defaults[flag_key] = hardcoded

    parser = make_parser()
    args, remaining = parser.parse_known_args()

    if remaining:
        # Trailing CLI args supply the query words.
        query = " ".join(remaining).strip()
    elif not sys.stdin.isatty():
        # Stdin pipe: read and parse for any embedded flags.
        raw = sys.stdin.read().strip()
        inner_args, inner_remaining = parser.parse_known_args(raw.split())
        merge_flags(args, inner_args)
        query = " ".join(inner_remaining).strip()
    else:
        # Interactive prompt.
        print("Ask your Spellbook a question, and it will search your notes to answer.")
        print('(Example: "what do I know about stoicism?" or "summarise my notes on philosophy")')
        print()
        raw = input("> ").strip()
        inner_args, inner_remaining = parser.parse_known_args(raw.split())
        merge_flags(args, inner_args)
        query = " ".join(inner_remaining).strip()

    if not query:
        sys.stderr.write("Error: query string is empty.\n")
        sys.exit(2)

    # Resolve final flag values: CLI-supplied > conf default > hardcoded default.
    no_wikis        = args.no_wikis        if args.no_wikis        is not None else conf_defaults["no_wikis"]
    no_zettels      = args.no_zettels      if args.no_zettels      is not None else conf_defaults["no_zettels"]
    include_sources = args.include_sources if args.include_sources is not None else conf_defaults["include_sources"]
    mode            = args.mode            if args.mode            is not None else conf_defaults["mode"]

    envelope = {
        "query": query,
        "flags": {
            "no_wikis":        no_wikis,
            "no_zettels":      no_zettels,
            "include_sources": include_sources,
            "mode":            mode,
        }
    }

    print(json.dumps(envelope))


if __name__ == "__main__":
    main()
