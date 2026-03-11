#!/usr/bin/env python3
"""
config_reader.py - Reads values from spellbook.conf.

Usage:
    python3 config_reader.py -s <section> -k <key>
    python3 config_reader.py -s spellbook -k inbox
    python3 config_reader.py -s spellbook -k notes

Options:
    -s, --section     Section name in spellbook.conf
    -k, --key         Key name within the section
    -c, --config      Path to spellbook.conf (auto-detected if omitted)
    --no-resolve      Do not resolve relative paths to absolute paths

Exit codes:
    0 - Success
    1 - Config file not found
    2 - Bad arguments
    3 - Section or key not found
"""

import sys
import os
import argparse
import configparser


def find_config(start_dir):
    """Search upward from start_dir for spellbook.conf."""
    current = os.path.abspath(start_dir)
    while True:
        candidate = os.path.join(current, "spellbook.conf")
        if os.path.isfile(candidate):
            return candidate
        parent = os.path.dirname(current)
        if parent == current:
            break
        current = parent
    return None


def parse_args():
    parser = argparse.ArgumentParser(
        description="Read values from spellbook.conf.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument("-s", "--section", required=True, help="Section name")
    parser.add_argument("-k", "--key", required=True, help="Key name")
    parser.add_argument("-c", "--config", default=None, help="Path to spellbook.conf")
    parser.add_argument(
        "--no-resolve",
        action="store_true",
        help="Do not resolve relative paths to absolute paths",
    )
    return parser.parse_args()


def load_config(config_path):
    """Parse spellbook.conf as an INI file."""
    config = configparser.RawConfigParser(allow_no_value=True)
    config.optionxform = str  # preserve key case
    config.read(config_path)
    return config


def main():
    args = parse_args()

    if args.config:
        config_path = args.config
        if not os.path.isfile(config_path):
            sys.stderr.write(f"Error: Config file not found: {config_path}\n")
            sys.exit(1)
    else:
        start = os.path.dirname(os.path.abspath(__file__))
        config_path = find_config(start)
        if not config_path:
            sys.stderr.write("Error: Could not find spellbook.conf\n")
            sys.exit(1)

    config = load_config(config_path)
    config_dir = os.path.dirname(config_path)

    if not config.has_section(args.section):
        sys.stderr.write(f"Error: Section [{args.section}] not found in config.\n")
        sys.exit(3)

    if not config.has_option(args.section, args.key):
        sys.stderr.write(
            f"Error: Key '{args.key}' not found in section [{args.section}].\n"
        )
        sys.exit(3)

    value = config.get(args.section, args.key)

    # Resolve relative paths for the [spellbook] section unless suppressed
    if not args.no_resolve and args.section == "spellbook":
        if value and not os.path.isabs(value):
            value = os.path.normpath(os.path.join(config_dir, value))

    print(value)


if __name__ == "__main__":
    main()
