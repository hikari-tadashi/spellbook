import sys
import json
import os
import requests

# cogito:8b seems to follow the rules better
MODEL = "cogito:8b"
API_URL = "http://localhost:11434/api/generate"
#NOTES_DIR = "./notes"
NOTES_DIR = "../../content/notes"

ALLOWED_TAGS = (
    "contacts, journal, messages, email, todo, calendar, alarm, science, technology, "
    "engineering, mathematics, fine-arts, music, History, philosophy, logic, computers, "
    "literature, movies, shows, family, friends, money, finances, business, project, code, other"
)

def get_tags(content):
    prompt = (
        f"Analyze this text and select tags strictly from this list: [{ALLOWED_TAGS}]. "
        "Avoid 'other' unless necessary. Use tags moderately. "
        "Return ONLY the selected tags formatted with hash signs (e.g. #science #logic)."
        f"\n\nText:\n{content}"
    )
    
    payload = {
        "model": MODEL,
        "prompt": prompt,
        "stream": False
    }
    
    try:
        response = requests.post(API_URL, json=payload)
        return response.json()['response'].strip()
    except Exception as e:
        sys.stderr.write(f"Tagging Error: {e}\n")
        return "#other"

def main():
    # Ensure notes directory exists
    os.makedirs(NOTES_DIR, exist_ok=True)

    # Read JSON input from pipe
    try:
        input_data = sys.stdin.read()
        zettels = json.loads(input_data)
    except json.JSONDecodeError:
        sys.stderr.write("Error: Invalid JSON input.\n")
        sys.exit(1)

    # Iterate, Tag, and Save
    for title, content in zettels.items():
        tags = get_tags(content)
        final_content = f"{content}\n\n{tags}"
        
        # Sanitize filename
        safe_title = "".join([c for c in title if c.isalpha() or c.isdigit() or c==' ']).rstrip()
        file_path = os.path.join(NOTES_DIR, f"{safe_title}.md")
        
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(final_content)
        
        print(f"Saved: {file_path}")

if __name__ == "__main__":
    main()