import os
import sys
import json
import shutil
import requests
import argparse

MODEL = "cogito:8b" 
API_URL = "http://localhost:11434/api/generate"

def parse_args():
    parser = argparse.ArgumentParser(description="Breaks text into atomic Zettelkasten notes using an LLM.")
    parser.add_argument("-m", "--metadata", type=json.loads, default={},
                        help="JSON dictionary of metadata to pass to the script.")
    return parser.parse_args()

def get_zettel_json(content):
    prompt = (
        "Break the following text into atomic Zettelkasten notes. "
        "Return ONLY a raw JSON list of strings, where each string is the content of an individual note. "
        "Do not include titles or keys. No markdown formatting, no explanations.\n\n"
        f"Text:\n{content}"
    )
    
    payload = {
        "model": MODEL,
        "prompt": prompt,
        "stream": False,
        "format": "json" 
    }
    
    try:
        response = requests.post(API_URL, json=payload)
        response.raise_for_status()
        return response.json()['response']
    except Exception as e:
        sys.stderr.write(f"LLM Call Error: {e}\n")
        sys.exit(1)

def flatten_llm_output(data):
    """Recursively extracts all strings from whatever messy JSON the LLM returns."""
    flat_list = []
    if isinstance(data, list):
        for item in data:
            flat_list.extend(flatten_llm_output(item))
    elif isinstance(data, dict):
        for value in data.values():
            flat_list.extend(flatten_llm_output(value))
    elif isinstance(data, str):
        # Only keep non-empty strings
        if data.strip():
            flat_list.append(data.strip())
    return flat_list

def main():
    args = parse_args()
    metadata = args.metadata
    
    # Read filename from argument or stdin
    try:
        # Note: sys.argv[1] might conflict with argparse if you use flags. 
        # Kept as you wrote it for now, assuming your workflow handles it.
        filepath = sys.argv[1].strip() if len(sys.argv) > 1 and not sys.argv[1].startswith('-') else sys.stdin.read().strip()
        with open(filepath, 'r', encoding='utf-8') as f:
            text_content = f.read()
            
        # Hacked move
        shutil.move(filepath, "/home/chris/Lab/spellbook/content/archive")
    except Exception as e:
        sys.stderr.write(f"File Error: {e}\n")
        sys.exit(1)

    # Get JSON from LLM
    zettel_json = get_zettel_json(text_content)
    
    try:
        # Parse the JSON string
        raw_data = json.loads(zettel_json)
        
        # Bulldoze the data into a flat 1D list of strings
        zettel_data = flatten_llm_output(raw_data)
        
        # Safety check: if the LLM completely blanked
        if not zettel_data:
            sys.stderr.write("Error: LLM returned empty data. Nothing to tag.\n")
            print("[]") # Pass empty JSON to the next pipe so it doesn't break
            sys.exit(0)
        
        # Extract just the filename from the path and format it
        filename = os.path.basename(filepath)
        formatted_filename = filename.replace(" ", "-")
        tag = f"#filename-{formatted_filename}"
        
        # Append the tag to the end of each note
        for i in range(len(zettel_data)):
            zettel_data[i] = f"{zettel_data[i]}\n\n{tag}"
            
        # Convert the list back to JSON and print to stdout
        print(json.dumps(zettel_data, indent=2))
        
    except json.JSONDecodeError:
        sys.stderr.write("Error: LLM output was not valid JSON.\n")
        print(json.dumps([])) # Output empty JSON list to prevent breaking pipelines

if __name__ == "__main__":
    main()