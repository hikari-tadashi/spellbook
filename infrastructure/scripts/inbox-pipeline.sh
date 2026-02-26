#!/bin/sh
python3 inbox_picker.py | python3 zettelkasten_llm.py | python3 zettel_id_generator.py | python3 tagger_llm.py