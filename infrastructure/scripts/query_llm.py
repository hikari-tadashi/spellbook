import sys
import json
import os
import subprocess
import argparse

MODEL = "cogito:8b"
HOST  = "http://localhost:11434"
ORACLE_CALL   = os.path.join(os.path.dirname(__file__), "oracle_call.py")
CONFIG_READER = os.path.join(os.path.dirname(__file__), "config_reader.py")


def get_config(section, key):
    result = subprocess.run(
        ["python3", CONFIG_READER, "-s", section, "-k", key],
        capture_output=True, text=True, check=True
    )
    return result.stdout.strip()


# Model resolution: query_llm_model > query_model > ollama_model > script default.
try:
    MODEL = get_config("spellbook", "query_llm_model")
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


SYSTEM_PROMPT = (
    "You are a knowledgeable assistant answering questions from a personal knowledge base.\n"
    "Answer the question using only the information provided in the context.\n"
    "Be concise and direct. Do not invent information not present in the context.\n"
    "If the context does not contain enough information to answer the question fully,\n"
    "say so clearly rather than speculating."
)


def main():
    parser = argparse.ArgumentParser(
        description="Generate the final response from the assembled context.")
    parser.add_argument("-o", "--mode", default="prose",
                        choices=["prose", "cited", "json"],
                        help="Output mode: prose, cited, or json (default: prose)")
    parser.add_argument("-m", "--metadata", type=json.loads, default={},
                        help="JSON dictionary of metadata (unused, required by convention)")
    args, _ = parser.parse_known_args()

    envelope = json.loads(sys.stdin.read())
    flags = envelope.get("flags", {})

    # Envelope flag takes precedence over ritual-file --mode arg.
    mode = flags.get("mode", args.mode)

    if mode == "json":
        envelope["response"] = ""
        print(json.dumps(envelope))
        return

    context = envelope.get("context", "")
    query   = envelope.get("query", "")

    user_prompt = f"{context}\n\nQuestion: {query}"

    if len(context.strip()) < 100:
        user_prompt = (
            "Note: the knowledge base returned no relevant content for this query.\n"
            "Answer based on general knowledge if possible, and note that this topic\n"
            "may not yet be covered in the Spellbook.\n\n"
        ) + user_prompt

    try:
        result = subprocess.run(
            ["python3", ORACLE_CALL, "-m", MODEL, "-H", HOST,
             "-s", SYSTEM_PROMPT, "-u", user_prompt],
            capture_output=True, text=True, check=True
        )
        response = result.stdout.strip()
    except subprocess.CalledProcessError as e:
        sys.stderr.write(f"Error: LLM call failed: {e.stderr}\n")
        sys.exit(1)

    envelope["response"] = response
    print(response)

    if mode == "cited":
        ranked_zettels = envelope.get("ranked_zettels", [])
        wikis          = envelope.get("wikis", [])

        print("\n## References")

        if ranked_zettels:
            print("\n**Notes:**")
            for z in ranked_zettels:
                print(f"- [[{z['id']}]]")

        if wikis:
            print("\n**Wikis:**")
            for w in wikis:
                print(f"- [[wiki/{w['tag']}]]")


if __name__ == "__main__":
    main()
