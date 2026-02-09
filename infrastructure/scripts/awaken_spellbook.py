import os
import sys
import shutil
from pathlib import Path

def create_spellbook_structure():
    # Define the root directory name
    root = "./"
    
    # List of directories to create (nested paths included)
    directories = [
        "content/archive",
        "content/assets",
        "content/journal",
        "content/maps/backlinks",
        "content/maps/tag-hubs",
        "content/notes",
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


    # TODO: move awaken_spellbook.py into infrastructure/scripts
    current_location = os.path.realpath(__file__)
    destination_dir = Path(root) / "infrastructure/scripts/"
    shutil.move(current_location, f"{destination_dir}/awaken.py")

    print("\nStructure setup complete!")

if __name__ == "__main__":
    create_spellbook_structure()