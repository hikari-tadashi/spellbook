import os
import sys

# Allow importing config_reader from the same directory
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from config_reader import find_config, load_config

def extract_key(line):
    """
    Extracts the key from a line by stripping out inline comments 
    and values (anything after '=').
    """
    # Remove inline comments (both # and ;)
    line = line.split('#')[0].split(';')[0]
    # Keep only the key if it's a key=value pair
    line = line.split('=')[0]
    # Return the cleaned string
    return line.strip()

def parse_spellbook_tags(filepath):
    """Reads the spellbook file and extracts tags from the [tags] section."""
    tags = set()
    in_tags_section = False
    
    if not os.path.exists(filepath):
        print(f"Warning: Spellbook file '{filepath}' not found.")
        return tags

    with open(filepath, 'r') as f:
        for line in f:
            line = line.strip()
            
            # Skip empty lines
            if not line:
                continue
            
            # Detect section headers
            if line.startswith('[') and line.endswith(']'):
                in_tags_section = (line == '[tags]')
                continue
            
            # If inside [tags] and not a full-line comment, extract the key
            if in_tags_section and not line.startswith(('#', ';')):
                tag = extract_key(line)
                if tag:
                    tags.add(tag)
                    
    return tags

def parse_extra_tags(filepath):
    """Reads the supplementary tags file and extracts keys."""
    tags = set()
    if not filepath or not os.path.exists(filepath):
        return tags
        
    with open(filepath, 'r') as f:
        for line in f:
            line = line.strip()
            # Skip empty lines and full-line comments
            if not line or line.startswith(('#', ';')):
                continue
                
            tag = extract_key(line)
            if tag:
                tags.add(tag)
                
    return tags

def process_tags(spellbook, tags_file, taghub):
    # 1. Parse both files
    spellbook_tags = parse_spellbook_tags(spellbook)
    extra_tags = parse_extra_tags(tags_file)
    
    # 2. Merge lists and remove duplicates (using a Python set automatically handles this)
    merged_tags = spellbook_tags.union(extra_tags)
    
    if not merged_tags:
        print("No tags found. Exiting.")
        return

    # 3. Ensure the taghub directory exists
    if not os.path.exists(taghub):
        os.makedirs(taghub)
        print(f"Created directory: {taghub}")
        
    # 4. Generate the tag-hub-{entryname} files
    for tag in merged_tags:
        file_path = os.path.join(taghub, f"tag-hub-{tag}")
        if not os.path.exists(file_path):
            with open(file_path, 'w') as f:
                pass # Creates an empty file
                
    # 5. Handle the canon-tags file
    canon_file = os.path.join(taghub, "canon-tags")
    existing_canon_tags = set()
    
    # Check what already exists in canon-tags to avoid duplicates
    if os.path.exists(canon_file):
        with open(canon_file, 'r') as f:
            for line in f:
                tag = line.strip()
                if tag:
                    existing_canon_tags.add(tag)
                    
    # Find only the tags that aren't already in the canon file
    new_tags_to_add = merged_tags - existing_canon_tags
    
    if new_tags_to_add:
        # Append only the new ones
        with open(canon_file, 'a') as f:
            for tag in sorted(new_tags_to_add):
                f.write(f"{tag}\n")
        print(f"Appended {len(new_tags_to_add)} new tags to '{canon_file}'.")
    else:
        print(f"No new tags needed to be added to '{canon_file}'.")

    print(f"Successfully processed a total of {len(merged_tags)} unique tags.")

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

    spellbook = _config_path
    tags = ''
    taghub = os.path.join(_resolve(_config.get('spellbook', 'maps')), 'tag-hub')

    process_tags(spellbook, tags, taghub)