#!/usr/bin/env python3
"""
ollama_call.py - A reusable Ollama API wrapper.

Usage:
    python3 ollama_call.py -m <model> -s <system_prompt> -u <user_prompt>
    echo "user prompt" | python3 ollama_call.py -m <model> -s <system_prompt>

Options:
    -m, --model     Model name (default: cogito:8b)
    -s, --system    System prompt string
    -u, --user      User prompt string (reads from stdin if omitted)
    -f, --format    Response format: 'json' or 'text' (default: text)
    -t, --timeout   Request timeout in seconds (default: 300)
    -H, --host      Ollama host URL (default: http://localhost:11434)

Exit codes:
    0 - Success
    1 - API or network error
    2 - Bad arguments
"""

import sys
import re
import argparse
import requests


DEFAULT_MODEL   = "cogito:8b"
DEFAULT_HOST    = "http://192.168.68.62:11434"
DEFAULT_TIMEOUT = 600


def parse_args():
    parser = argparse.ArgumentParser(
        description="Shell-out wrapper for Ollama API calls.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )
    parser.add_argument("-m", "--model",
                        default=DEFAULT_MODEL,
                        help=f"Model to use (default: {DEFAULT_MODEL})")
    parser.add_argument("-s", "--system",
                        default="",
                        help="System prompt")
    parser.add_argument("-u", "--user",
                        default=None,
                        help="User prompt (reads from stdin if omitted)")
    parser.add_argument("-f", "--format",
                        choices=["json", "text"],
                        default="text",
                        help="Response format: 'json' or 'text' (default: text)")
    parser.add_argument("-t", "--timeout",
                        type=int,
                        default=DEFAULT_TIMEOUT,
                        help=f"Request timeout in seconds (default: {DEFAULT_TIMEOUT})")
    parser.add_argument("-H", "--host",
                        default=DEFAULT_HOST,
                        help=f"Ollama host URL (default: {DEFAULT_HOST})")
    parser.add_argument("-T", "--think",
                        action="store_true",
                        default=False,
                        help="Enable thinking mode (e.g. for Qwen3 reasoning models)")
    return parser.parse_args()


def call_ollama(model, system_prompt, user_prompt, fmt, timeout, host, think=False):
    url = f"{host}/api/generate"

    payload = {
        "model":  model,
        "prompt": user_prompt,
        "stream": False,
    }

    if system_prompt:
        payload["system"] = system_prompt

    if fmt == "json":
        payload["format"] = "json"

    payload["options"] = {"think": think}

    try:
        response = requests.post(url, json=payload, timeout=timeout)
        response.raise_for_status()
    except requests.exceptions.ConnectionError:
        sys.stderr.write(f"Error: Could not connect to Ollama at {host}. Is it running?\n")
        sys.exit(1)
    except requests.exceptions.Timeout:
        sys.stderr.write(f"Error: Request timed out after {timeout}s.\n")
        sys.exit(1)
    except requests.exceptions.HTTPError as e:
        sys.stderr.write(f"Error: HTTP {response.status_code} - {e}\n")
        sys.exit(1)

    try:
        data = response.json()
    except ValueError:
        sys.stderr.write("Error: Could not parse Ollama response as JSON.\n")
        sys.exit(1)

    response_text = data.get("response", "")
    # Strip <think>...</think> blocks produced by reasoning models (e.g. Qwen3)
    # To enable explicit thinking mode via the Ollama API, add "options": {"think": True}
    # to the payload above and pass it through a --think flag.
    response_text = re.sub(r"<think>.*?</think>", "", response_text, flags=re.DOTALL).strip()
    return response_text


def main():
    args = parse_args()

    # Resolve user prompt: flag → stdin → error
    user_prompt = args.user
    if user_prompt is None:
        if not sys.stdin.isatty():
            user_prompt = sys.stdin.read().strip()
        else:
            sys.stderr.write("Error: No user prompt provided via -u/--user or stdin.\n")
            sys.exit(2)

    if not user_prompt:
        sys.stderr.write("Error: User prompt is empty.\n")
        sys.exit(2)

    result = call_ollama(
        model=args.model,
        system_prompt=args.system,
        user_prompt=user_prompt,
        fmt=args.format,
        timeout=args.timeout,
        host=args.host,
        think=args.think,
    )

    print(result)


if __name__ == "__main__":
    main()
