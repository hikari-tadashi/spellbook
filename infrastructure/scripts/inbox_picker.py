import os
import random
import sys

# Configuration
INBOX_DIR = "../../inbox"
EXTENSIONS = {".md", ".txt"}

def main():
    # Ensure inbox exists
    if not os.path.exists(INBOX_DIR):
        sys.stderr.write(f"Error: Directory '{INBOX_DIR}' not found.\n")
        sys.exit(1)

    # Filter files
    files = [
        f for f in os.listdir(INBOX_DIR) 
        if os.path.isfile(os.path.join(INBOX_DIR, f)) 
        and os.path.splitext(f)[1].lower() in EXTENSIONS
    ]

    if not files:
        sys.stderr.write("Error: No markdown or text files in inbox.\n")
        sys.exit(1)

    # Pick random file and print absolute path to stdout
    selected_file = os.path.join(INBOX_DIR, random.choice(files))
    print(selected_file)

if __name__ == "__main__":
    main()