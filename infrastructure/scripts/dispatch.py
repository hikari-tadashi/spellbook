#!/usr/bin/env python3
"""
dispatch.py — Routes inbox content to the appropriate absorber and normalizes
output to a JSON list of zettel strings for the downstream pipeline.

Reads a file path or folder path from stdin.
- Folders  → shelf_absorber.py  (or a registered plugin handler)
- Files    → zettelkasten_llm.py (or a registered plugin handler)

In both cases, the absorber's stdout (a JSON list) is forwarded to dispatch's
stdout so that zettel_id_generator.py and tagger_llm.py can continue normally.

Plugin handler registration (in plugin.conf):
  [dispatch]
  handles_folders = scripts/my_folder_handler.py
  handles_files   = scripts/my_file_handler.py
"""

import os
import sys
import subprocess

SCRIPT_DIR        = os.path.dirname(os.path.abspath(__file__))
CONFIG_READER     = os.path.join(SCRIPT_DIR, "config_reader.py")
ZETTELKASTEN_LLM  = os.path.join(SCRIPT_DIR, "zettelkasten_llm.py")
SHELF_ABSORBER    = os.path.join(SCRIPT_DIR, "shelf_absorber.py")
UNKNOWN_ABSORBER  = os.path.join(SCRIPT_DIR, "unknown_absorber.py")

# Extensions dispatch treats as readable text and routes to zettelkasten_llm.py.
# Anything else goes to unknown_absorber.py, which files it and records its arrival.
TEXT_EXTENSIONS = {".txt", ".md", ".markdown", ".rst", ".org", ".text"}


def get_config(section, key):
    result = subprocess.run(
        ["python3", CONFIG_READER, "-s", section, "-k", key],
        capture_output=True, text=True
    )
    if result.returncode != 0:
        return None
    return result.stdout.strip() or None


def find_plugin_handler(handler_key):
    """
    Scan infrastructure/plugins/ for a plugin.conf that declares a handler
    under [dispatch]. Returns the resolved absolute path to the handler script,
    or None if no plugin claims it.
    """
    root = get_config("spellbook", "root")
    if not root:
        return None

    plugins_dir = os.path.join(root, "infrastructure", "plugins")
    if not os.path.isdir(plugins_dir):
        return None

    for entry in sorted(os.listdir(plugins_dir)):  # alphabetical for determinism
        plugin_dir = os.path.join(plugins_dir, entry)
        if not os.path.isdir(plugin_dir):
            continue
        conf_path = os.path.join(plugin_dir, "plugin.conf")
        if not os.path.isfile(conf_path):
            continue

        in_dispatch = False
        with open(conf_path) as f:
            for line in f:
                line = line.strip()
                if line.startswith("["):
                    in_dispatch = (line == "[dispatch]")
                    continue
                if in_dispatch and "=" in line:
                    key, _, val = line.partition("=")
                    if key.strip() == handler_key and val.strip():
                        handler_path = os.path.join(plugin_dir, val.strip())
                        if os.path.isfile(handler_path):
                            return handler_path
    return None


def run_absorber(script_path, target_path):
    """
    Call an absorber with target_path on stdin. Forward its stdout to our own
    stdout so the downstream pipeline receives the JSON list.
    """
    result = subprocess.run(
        ["python3", script_path],
        input=target_path,
        text=True,
        capture_output=True
    )
    if result.returncode != 0:
        sys.stderr.write(
            f"dispatch.py: absorber '{os.path.basename(script_path)}' exited "
            f"with code {result.returncode} for '{target_path}'\n"
        )
        if result.stderr:
            sys.stderr.write(result.stderr)
        sys.exit(result.returncode)

    # Forward stderr (progress messages) and stdout (JSON) separately
    if result.stderr:
        sys.stderr.write(result.stderr)
    print(result.stdout, end="")


def main():
    path = sys.stdin.read().strip()
    if not path:
        sys.exit(0)

    if not os.path.exists(path):
        sys.stderr.write(f"dispatch.py: path does not exist: '{path}'\n")
        sys.exit(1)

    if os.path.isdir(path):
        handler = find_plugin_handler("handles_folders") or SHELF_ABSORBER
        run_absorber(handler, path)
    else:
        plugin_handler = find_plugin_handler("handles_files")
        if plugin_handler:
            run_absorber(plugin_handler, path)
        else:
            ext = os.path.splitext(path)[1].lower()
            if ext in TEXT_EXTENSIONS:
                run_absorber(ZETTELKASTEN_LLM, path)
            else:
                run_absorber(UNKNOWN_ABSORBER, path)


if __name__ == "__main__":
    main()
