import sys
import json
import shutil
import requests

MODEL = "cogito:8b" # User specified Llama3.1:8b
API_URL = "http://localhost:11434/api/generate"

def get_zettel_json(content):
    prompt = (
        "Break the following text into atomic Zettelkasten notes. "
        "Return ONLY a raw JSON dictionary where keys are titles and values are content. "
        "No markdown formatting, no explanations.\n\n"
        f"Text:\n{content}"
    )
    
    payload = {
        "model": MODEL,
        "prompt": prompt,
        "stream": False,
        "format": "json" # Enforces JSON mode in Ollama
    }
    
    try:
        response = requests.post(API_URL, json=payload)
        response.raise_for_status()
        return response.json()['response']
    except Exception as e:
        sys.stderr.write(f"LLM Call Error: {e}\n")
        sys.exit(1)

def main():
    # Read filename from argument or stdin
    try:
        filepath = sys.argv[1].strip() if len(sys.argv) > 1 else sys.stdin.read().strip()
        with open(filepath, 'r', encoding='utf-8') as f:
            text_content = f.read()
            # This is hacked in by me just for a quick test, but should be a standalone process in the pipeline
            f.close()
            shutil.move(filepath, "../../content/archive")
            #os.remove(filepath)
    except Exception as e:
        sys.stderr.write(f"File Error: {e}\n")
        sys.exit(1)

    # Get JSON from LLM and print to stdout for the next pipe
    zettel_json = get_zettel_json(text_content)
    print(zettel_json)

if __name__ == "__main__":
    main()