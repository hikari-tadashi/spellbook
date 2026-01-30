import os
from pathlib import Path

def create_spellbook_structure():
    # Define the root directory name
    root = "content"
    
    # List of directories to create (nested paths included)
    directories = [
        "archive",
        "assets",
        "journal",
        "maps/backlinks",
        "maps/hubs",
        "maps/notes",
        "inbox",
        "infrastructure/documentation",
        "infrastructure/scripts",
        "projects"
    ]
    
    # List of files to create in the root
    files = [
        #"Dashboard.md",
        "README.md",
        "spellbook.conf"
    ]

    print(f"--- Initializing structure in: {os.path.abspath(root)} ---")

    # 1. Create Directories
    for folder in directories:
        dir_path = Path(root) / folder
        dir_path.mkdir(parents=True, exist_ok=True)
        print(f"Checked folder: {dir_path}")

    # 2. Create Files
    for file_name in files:
        file_path = Path(root) / file_name
        if not file_path.exists():
            file_path.touch()
            print(f"Created file: {file_path}")
        else:
            print(f"File already exists: {file_path}")

    print("\nStructure setup complete!")

if __name__ == "__main__":
    create_spellbook_structure()