#!/usr/bin/env python3
"""
oracle_call.py - Oracle backend dispatcher.

Reads oracle_backend from [spellbook] conf and delegates to the appropriate
backend script (ollama_call.py or call_lmstudio.py), passing all arguments
through unchanged.

Usage: identical to ollama_call.py and call_lmstudio.py.

oracle_backend values:
  ollama     → ollama_call.py    (default if key absent)
  lmstudio   → call_lmstudio.py

Exit codes mirror those of the delegated script.
"""

import sys
import os
import subprocess

SCRIPT_DIR    = os.path.dirname(os.path.abspath(__file__))
CONFIG_READER = os.path.join(SCRIPT_DIR, "config_reader.py")

BACKENDS = {
    "ollama":   "ollama_call.py",
    "lmstudio": "call_lmstudio.py",
}


def get_backend():
    result = subprocess.run(
        ["python3", CONFIG_READER, "-s", "spellbook", "-k", "oracle_backend"],
        capture_output=True, text=True
    )
    if result.returncode == 3:   # key not found — use default silently
        return "ollama"
    if result.returncode != 0:
        sys.stderr.write(f"Error: config_reader failed: {result.stderr.strip()}\n")
        sys.exit(1)
    return result.stdout.strip() or "ollama"


def main():
    backend = get_backend()
    if backend not in BACKENDS:
        sys.stderr.write(
            f"Error: Unknown oracle_backend '{backend}'. "
            f"Valid values: {', '.join(BACKENDS)}\n"
        )
        sys.exit(1)

    target = os.path.join(SCRIPT_DIR, BACKENDS[backend])
    result = subprocess.run(
        ["python3", target] + sys.argv[1:],
        # stdout and stderr inherited — caller sees output directly
    )
    sys.exit(result.returncode)


if __name__ == "__main__":
    main()
