# TODO: this should a ritual rather than a single script.
import os
import re
import shutil
import datetime
import subprocess

OLLAMA_CALL = os.path.join(os.path.dirname(__file__), "ollama_call.py")
CONFIG_READER = os.path.join(os.path.dirname(__file__), "config_reader.py")

def get_config(section, key):
    result = subprocess.run(
        ["python3", CONFIG_READER, "-s", section, "-k", key],
        capture_output=True, text=True, check=True
    )
    return result.stdout.strip()

def get_timestamp():
    """Returns a formatted timestamp: YYYYMMDDHHMMSS"""
    return datetime.datetime.now().strftime("%Y%m%d%H%M%S")

def archive_existing_wiki(wiki_filepath, archive_dir, tag):
    """Moves an existing wiki to the archive directory with a timestamp."""
    if os.path.exists(wiki_filepath):
        if not os.path.exists(archive_dir):
            os.makedirs(archive_dir)
            print(f"Created archive directory: {archive_dir}")
        
        timestamp = get_timestamp()
        archived_filename = f"{tag}_{timestamp}.md"
        archived_filepath = os.path.join(archive_dir, archived_filename)
        
        shutil.move(wiki_filepath, archived_filepath)
        print(f"Archived existing wiki for '{tag}' to {archived_filepath}")

def extract_source_path(note_filepath):
    """Extracts the path from a 'Source: [[path/to/file]]' string."""
    try:
        with open(note_filepath, 'r', encoding='utf-8') as f:
            content = f.read()
            
        # Regex looks for "Source: [[" followed by anything, ending with "]]"
        match = re.search(r'Source:\s*\[\[(.*?)\]\]', content, re.IGNORECASE)
        if match:
            return match.group(1).strip()
        else:
            return None
    except Exception as e:
        print(f"  Error reading note {note_filepath}: {e}")
        return None

def append_error_tag(note_filepath):
    """Appends an #error tag to a note if it's missing a valid source link."""
    try:
        with open(note_filepath, 'a', encoding='utf-8') as f:
            f.write("\n#error\n")
        print(f"  Appended #error tag to {note_filepath}")
    except Exception as e:
        print(f"  Failed to append error to {note_filepath}: {e}")

def call_ollama(tag, source_texts, model, host):
    """Sends the aggregated texts to Ollama to generate a wiki."""
    compiled_sources = "\n\n--- NEXT SOURCE ---\n\n".join(source_texts)

    prompt = (
        f"Please write a comprehensive, well-structured wiki page about the topic / tag: \"#{tag}\". "
        f"Use Obsidian Markdown format. Base your wiki entirely on the following source texts provided below. "
        f"Do not invent information outside of these sources.\n\nSOURCE TEXTS:\n{compiled_sources}"
    )

    print(f"  Sending request to Ollama (Model: {model}) for tag '{tag}'...")
    try:
        result = subprocess.run(
            ["python3", OLLAMA_CALL, "-m", model, "-H", host,
             "-s", "You are an expert knowledge base curator. Write in Obsidian Markdown format."],
            input=prompt, capture_output=True, text=True, check=True
        )
        return result.stdout
    except subprocess.CalledProcessError as e:
        print(f"  API Error for tag '{tag}': {e.stderr}")
        return None

def process_wikis(canon_file, taghub_dir, notes_dir, wiki_dir, archive_dir, ollama_model, ollama_host):
    if not os.path.exists(canon_file):
        print(f"Error: Canon file '{canon_file}' not found.")
        return

    if not os.path.exists(wiki_dir):
        os.makedirs(wiki_dir)

    # 1. Read tags from canon file
    with open(canon_file, 'r', encoding='utf-8') as f:
        tags = [line.strip() for line in f if line.strip()]

    # 2. Iterate through each tag
    for tag in tags:
        print(f"\nProcessing tag: {tag}")
        wiki_filepath = os.path.join(wiki_dir, f"{tag}.md")
        taghub_filepath = os.path.join(taghub_dir, f"tag-hub-{tag}")
        
        # Archive existing wiki if it exists
        archive_existing_wiki(wiki_filepath, archive_dir, tag)
        
        if not os.path.exists(taghub_filepath):
            print(f"  No tag-hub file found for '{tag}'. Skipping.")
            continue
            
        source_texts = []
        zettels_used = []
        original_sources_used = []
        
        # 3. Read notes listed in the tag-hub file
        with open(taghub_filepath, 'r', encoding='utf-8') as f:
            note_files = [line.strip() for line in f if line.strip()]
            
        for note_file in note_files:
            note_filepath = os.path.join(notes_dir, note_file)
            if not os.path.exists(note_filepath):
                print(f"  Note '{note_file}' not found. Skipping.")
                continue
                
            # 4. Extract Source link
            source_path = extract_source_path(note_filepath)
            
            if not source_path:
                print(f"  No 'Source: [[...]]' found in {note_file}.")
                append_error_tag(note_filepath)
                continue
                
            # 5. Open the extracted source file
            if os.path.exists(source_path):
                try:
                    with open(source_path, 'r', encoding='utf-8') as src_f:
                        source_texts.append(src_f.read())
                        zettels_used.append(note_file)
                        original_sources_used.append(source_path)
                except Exception as e:
                    print(f"  Error reading source file '{source_path}': {e}")
            else:
                print(f"  Source file '{source_path}' does not exist on disk.")
                
        # 6. Generate Wiki via Ollama
        if not source_texts:
            print(f"  No valid source texts found for '{tag}'. Skipping wiki generation.")
            continue
            
        generated_wiki = call_ollama(tag, source_texts, ollama_model, ollama_host)
        
        if generated_wiki:
            # 7. Append References Footer
            footer = "\n\n---\n## References\n\n**Zettels Used:**\n"
            for zettel in set(zettels_used): # Remove duplicates just in case
                footer += f"- [[{zettel.replace('.md', '')}]]\n"
                
            footer += "\n**Original Sources:**\n"
            for src in set(original_sources_used):
                # Clean up path to just the filename for cleaner Obsidian linking
                clean_src = os.path.basename(src).replace('.md', '')
                footer += f"- [[{clean_src}]]\n"
                
            final_content = generated_wiki + footer
            
            # 8. Save the new wiki
            with open(wiki_filepath, 'w', encoding='utf-8') as f:
                f.write(final_content)
            print(f"  Successfully created wiki: {wiki_filepath}")

if __name__ == "__main__":
    taghub_dir  = get_config("spellbook", "taghub")
    notes_dir   = get_config("spellbook", "notes")
    wiki_dir    = get_config("spellbook", "wiki")
    archive_dir = os.path.join(get_config("spellbook", "archive"), "wiki")
    canon_file  = os.path.join(taghub_dir, "canon-tags")
    try:
        ollama_model = get_config("spellbook", "wiki_model")
    except subprocess.CalledProcessError:
        try:
            ollama_model = get_config("spellbook", "ollama_model")
        except subprocess.CalledProcessError:
            ollama_model = 'cogito:8b'

    try:
        _host = get_config("spellbook", "ollama_host")
        ollama_host = _host if _host.startswith("http") else f"http://{_host}"
    except subprocess.CalledProcessError:
        ollama_host = "http://localhost:11434"

    process_wikis(canon_file, taghub_dir, notes_dir, wiki_dir, archive_dir, ollama_model, ollama_host)