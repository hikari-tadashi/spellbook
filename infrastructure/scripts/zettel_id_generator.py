import sys
import json
from datetime import datetime, timedelta

def main():
    # Read the JSON list from standard input (passed from zettelkasten_llm.py)
    try:
        input_data = sys.stdin.read().strip()
        if not input_data:
            sys.exit(0) # Exit silently if no input is provided
            
        zettel_list = json.loads(input_data)
        
        if not isinstance(zettel_list, list):
            sys.stderr.write("Error: Expected a JSON list from stdin.\n")
            sys.exit(1)
            
    except json.JSONDecodeError:
        # Fixed the filename in the error output
        sys.stderr.write("Error: Invalid JSON received in zettel_id_generator.py.\n")
        sys.exit(1)

    zettel_dict = {}
    
    # Grab the initial time. We will increment this in the loop.
    current_time = datetime.now()

    # Iterate through the list and convert each entry into a key-value dictionary entry
    for content in zettel_list:
        # Generate standard 14-digit Zettelkasten ID: YYYYMMDDHHMMSS
        note_key = current_time.strftime("%Y%m%d%H%M%S")
        
        # Add to the dictionary where the timestamp is the key and the list item is the value
        zettel_dict[note_key] = content
        
        # Increment by 1 second to guarantee the next key is uniquely timestamped
        current_time += timedelta(seconds=1)

    # Print the resulting dictionary as a JSON string to stdout for tagger_llm.py
    print(json.dumps(zettel_dict, indent=2))

if __name__ == "__main__":
    main()