import os
import re
import sys
from collections import defaultdict

# Allow importing config_reader from the same directory
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from config_reader import find_config, load_config

def scan_notes_for_tags(canon_file, notes_dir, taghub_dir):
    # 1. Load canonical tags
    canon_tags = set()
    if os.path.exists(canon_file):
        with open(canon_file, 'r', encoding='utf-8') as f:
            for line in f:
                tag = line.strip()
                if tag:
                    canon_tags.add(tag)
    else:
        print(f"Error: '{canon_file}' not found. Please run the tag generator script first.")
        return

    # 2. Initialize data structures
    # A dictionary where each key is a tag, and the value is a set of filenames (prevents duplicates)
    tag_to_files = defaultdict(set)
    non_canon_tags = set()

    # Regex pattern to find tags like #journal, #fine-arts, #todo
    # It looks for a '#' preceded by a space or the start of a line, 
    # followed by word characters, numbers, underscores, or hyphens.
    tag_pattern = re.compile(r'(?:^|\s)#([\w\-]+)')

    # 3. Check if notes directory exists
    if not os.path.exists(notes_dir):
        print(f"Error: Notes directory '{notes_dir}' not found.")
        return

    # 4. Scan through all files in the notes directory
    print(f"Scanning files in '{notes_dir}'...")
    for root, _, files in os.walk(notes_dir):
        for filename in files:
            filepath = os.path.join(root, filename)
            
            # Use a try-except block to safely ignore binary or non-text files
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    content = f.read()
                    
                    # Extract all #tags found in the document
                    found_tags = tag_pattern.findall(content)
                    
                    for tag in found_tags:
                        if tag in canon_tags:
                            # It's a known tag, add the filename to the set
                            tag_to_files[tag].add(filename)
                        elif not tag.startswith('filename-'):
                            # It's an unrecognized tag, add it to the non-canon list
                            non_canon_tags.add(tag)
                            
            except (UnicodeDecodeError, IsADirectoryError):
                # Skip files that can't be read as plain text
                continue

    # 5. Populate the tag-hub files
    if not os.path.exists(taghub_dir):
        os.makedirs(taghub_dir)

    for tag, files_set in tag_to_files.items():
        hub_filepath = os.path.join(taghub_dir, f"tag-hub-{tag}")
        with open(hub_filepath, 'w', encoding='utf-8') as f:
            for fname in sorted(files_set):
                f.write(f"{fname}\n")
                
    # 6. Generate the non-canon-tags file
    non_canon_file = os.path.join(taghub_dir, 'non-canon-tags')
    with open(non_canon_file, 'w', encoding='utf-8') as f:
        for tag in sorted(non_canon_tags):
            f.write(f"{tag}\n")

    # Print summary
    print(f"Updated {len(tag_to_files)} 'tag-hub-*' files in '{taghub_dir}'.")
    print(f"Found {len(non_canon_tags)} unrecognized tags. Written to '{non_canon_file}'.")

if __name__ == "__main__":
    _config_path = find_config(os.path.dirname(os.path.abspath(__file__)))
    if not _config_path:
        print("Error: Could not find spellbook.conf")
        sys.exit(1)
    _config = load_config(_config_path)
    _config_dir = os.path.dirname(_config_path)

    def _resolve(val):
        if val and not os.path.isabs(val):
            return os.path.normpath(os.path.join(_config_dir, val))
        return val

    _maps = _resolve(_config.get('spellbook', 'maps'))
    canon_file = os.path.join(_maps, 'tag-hub', 'canon-tags')
    notes_dir = _resolve(_config.get('spellbook', 'notes'))
    taghub_dir = os.path.join(_maps, 'tag-hub')

    scan_notes_for_tags(canon_file, notes_dir, taghub_dir)