# ✦ THE SPELLBOOK ✦
**An LLM created Personal Knowledge Base**
─────────────────────────────
*Narrated by the Install Wizard* *whose robes are singed, whose patience is vast,* *and whose chief concern is that you succeed.*

## A Note from Your Wizard
Ah. You've opened the manual. Good. That already puts you ahead of most apprentices, who prefer to learn by setting things on fire. I am the Install Wizard. You may have met me briefly when you first ran the Spellbook installer — I was the one asking you where you wanted your library and which oracle you preferred. I am, in the tradition of wizards everywhere, both a guide and a piece of software.

This manual will teach you how the Spellbook works, what all its peculiar pieces do, and — when you're ready — how to extend it with your own rituals. Nothing here will be forced on you. Each section offers understanding first, and action only when you want it. If you are new to software and feel uncertain: good. Uncertainty means you're paying attention. I'll explain everything, and I'll never assume you know something I haven't taught you yet. Now. Let us begin.

This document is divided into six parts:
* **Part I** explains what the Spellbook is and why it works the way it does.
* **Part II** covers the physical structure — the files and folders.
* **Part III** walks through the ritual cycle, which is the heart of the system.
* **Part IV** teaches you how to write your own rituals.
* **Part V** covers your Obsidian vault — the interface where your knowledge lives.
* **Part VI** introduces the plugin system — how to extend the Spellbook with your own components.

A reference section and glossary follow at the end. You do not need to read this linearly. It is a reference as much as it is a guide. But if you are new, Parts I and II are worth reading in order.

---

## Part I — The World of the Spellbook
### What Is the Spellbook?
A spellbook, in folklore, is not merely a book of spells. It is a personal record of a practitioner's accumulated knowledge — observations, experiments, correspondences, sources. It is a living document. The spellbook grows with the wizard.

The Spellbook is a personal knowledge management system. That is a formal way of saying it is a place where you put things you want to remember, and software that helps you organise, connect, and retrieve them. You drop a document, a note, or a piece of writing into your inbox. The Spellbook reads it, breaks it into focused ideas, tags those ideas, and files them. Over time, it builds an interconnected web of knowledge — a graph of everything you've fed it, linked by topic.

The system is designed to run locally, on your own computer. Your notes never leave your machine unless you choose to put them somewhere. The artificial intelligence it uses — which handles the reading, organising, and writing — runs locally, through either Ollama or LM Studio, both of which keep your text entirely on your own hardware. Which backend is active at any given moment is a single line in your configuration file.

The Spellbook is used through **Obsidian**, a free note-taking application that reads a folder of text files and displays them as an interconnected knowledge base. Obsidian is the lens through which you read and navigate your Spellbook. The Spellbook's scripts produce the files; Obsidian displays them.

### The Language of the Spellbook
Every craft has its vocabulary. A carpenter speaks of joinery; a physician speaks of anatomy. The Spellbook's vocabulary borrows from the language of magic — not to be whimsical for its own sake, but because these metaphors map cleanly onto the underlying concepts. Once you understand the map, both the folklore and the software become easier to navigate at once.

The table below shows the Spellbook's terms alongside their plain-language meanings and their precise technical definitions. When you encounter an unfamiliar word in this manual, return here.

| Spellbook Term | In Plain English | What It Actually Is |
| :--- | :--- | :--- |
| Spellbook | Your knowledge base | The entire system: software, files, and configuration together |
| Grimoire | Your personal library | Your installation directory — the folder containing everything |
| Ritual | An automated task | A plain text file listing shell commands to run in sequence |
| Script | A helper program | A file containing code (Python, Clojure, or any language) that does one specific job |
| Spell | A command you cast | A single command line executed during a ritual |
| Inbox | Your input tray | A folder where you drop raw notes and documents to be processed |
| Zettel | An atomic idea | A single, self-contained note — one idea per note |
| Tag Hub | A topic index | A generated file listing every note connected to a given tag |
| Wiki | A topic summary | An AI-generated overview of a topic, drawn from all your notes on it |
| Oracle | Your AI assistant | The local AI that reads and writes on your behalf — routed through `oracle_call.py` to either Ollama or LM Studio |
| Model | The oracle's knowledge | The specific AI language model loaded into your chosen backend |
| Configuration Tome | Your settings file | `spellbook.conf` — an INI file that tells the system where everything lives |
| Install Wizard | The setup guide | The installation script — and, by extension, this narrator |
| Canon Tags | Your approved vocabulary | A list of tags the system recognises as valid for categorisation |
| Archive | Processed storage | A folder where original files are moved after being processed |
| Shelf | Long-term folder storage | A folder moved intact to `content/shelves/`, preserved in its original structure with an anchor zettel linking back to it |
| Absorber | A content handler | A script that receives inbox content and converts it into zettel-ready JSON — either built-in or registered by a plugin |
| Pipeline | A chain of steps | A sequence of programs where each one's output feeds the next's input |

### The Architecture at a Glance
Before we descend into the details, let me show you the whole shape of the thing. A map is worth ten descriptions of individual roads.

The Spellbook's architecture has three layers, each built on top of the previous one.
* **The first layer is the file system.** Your notes, your scripts, your rituals, your configuration — everything is a plain text file in a regular folder. There is no database. There is no cloud service. If you can read a text file, you can see exactly what the Spellbook is doing.
* **The second layer is the runtime.** This is the Babashka interpreter — a small, portable program that can read and execute Clojure code on any operating system. Babashka is why the Spellbook works the same way on Windows, Mac, and Linux without modification. Clojure is a dialect of Lisp, a family of programming languages known for their elegance. You do not need to know Clojure to use the Spellbook. You only need to know that Babashka is the engine that turns rituals into action.
* **The third layer is the oracle.** This is the local AI. The Spellbook calls on the oracle to perform three tasks: breaking documents into atomic notes, assigning tags to those notes, and generating wiki pages from groups of notes. The oracle layer is an abstraction: a dispatcher script called `oracle_call.py` reads your chosen backend from `spellbook.conf` and routes every AI request to either **Ollama** or **LM Studio** accordingly. Both run on your machine. Neither sends your text to the internet. Switching backends is a one-line change in your config.

The flow of information through the system looks like this:

```text
[ Your raw notes and folders ]
│
▼
[ inbox/ folder ] ← You drop files and folders here
│
▼ (absorb ritual)
[ dispatch: file? → Oracle breaks text into Zettels ]
[           folder? → Oracle writes an anchor zettel, folder moves to shelves/ ]
│
▼ (Oracle assigns tags)
[ content/notes/ ] ← Atomic, tagged notes
│
▼ (focus ritual)
[ content/maps/tag-hub/ ] ← Tag index built
│
▼ (sleep / wiki ritual)
[ content/maps/wiki/ ] ← Wiki pages written
│
▼
[ Obsidian vault ] ← You browse and read here
         │
         ▼ (query / query-cited ritual)
[ Oracle answers your questions ]  ← Ask anything
```

*(The oracle layer — `oracle_call.py` — sits between every ritual and the AI backend. Set `oracle_backend = ollama` or `oracle_backend = lmstudio` in your conf to choose which engine powers the oracle at any time.)*

---

## Part II — The Grimoire
### Your Directory Structure
Every great library needs a consistent architecture. A book left in the wrong room is, for all practical purposes, lost. The Spellbook's directory structure is not arbitrary — each folder has a single purpose, and understanding that purpose will help you navigate your installation confidently.

When you installed the Spellbook, the Install Wizard created the following folder structure inside your chosen installation directory. Here it is in full, with annotations:

```text
spellbook/ ← Your grimoire root
├── inbox/ ← Drop raw notes and folders here
├── content/
│ ├── notes/ ← Processed atomic notes (Zettels)
│ ├── archive/ ← Original files after processing
│ ├── shelves/ ← Folders moved here intact, each with an anchor zettel
│ ├── assets/
│ │ ├── media/ ← Audio, video, and image files filed from inbox
│ │ └── data/  ← PDFs, documents, and other non-text files filed from inbox
│ ├── journal/ ← Journal entries (moved here via command)
│ └── maps/ ← Generated knowledge maps
│ ├── tag-hub/ ← Tag index files
│ ├── wiki/ ← AI-generated wiki pages
│ ├── hubs/ ← Other hub files
│ └── backlinks/ ← Backlink index files
├── infrastructure/
│ ├── scripts/ ← The programs that run the system
│ ├── rituals/ ← The ritual files you invoke
│ ├── plugins/ ← Optional extensions to the system
│ └── docs/ ← This manual and other documentation
├── projects/ ← Project-specific notes (optional)
└── spellbook.conf ← Your configuration tome
```
*(Structure defined in)*

The most important thing to understand is the distinction between `content/` and `infrastructure/`.
* Everything in `content/` is yours — your notes, your knowledge, your archive.
* Everything in `infrastructure/` is the machinery of the system. You will read from infrastructure; the system writes to content.

The `inbox/` folder is the entry point. It stands apart at the root level because it is the one folder you interact with directly, every day. Drop a file in. The system handles the rest.

### The Configuration Tome — spellbook.conf
In a real grimoire, the first pages describe the practitioner's particulars — their location, their preferred materials, their allegiances. The Spellbook's configuration file serves the same purpose. It tells every part of the system where things are and how you prefer to work.

The file `spellbook.conf` lives at the root of your installation. It is a plain text file, readable in any text editor. It is divided into sections, each marked with a name in square brackets. Within each section, settings are written as `key = value` pairs. Lines beginning with `;` or `#` are comments — notes to yourself that the system ignores.

Here is what a typical `spellbook.conf` looks like, with explanations of each section:

```ini
; ── [spellbook] — core paths and oracle settings ──────────────────────────────
[spellbook]
root = /home/yourname/Documents/spellbook
inbox = /home/yourname/Documents/spellbook/inbox
notes = /home/yourname/Documents/spellbook/content/notes
archive = /home/yourname/Documents/spellbook/content/archive
maps = /home/yourname/Documents/spellbook/content/maps
taghub = /home/yourname/Documents/spellbook/content/maps/tag-hub
wiki = /home/yourname/Documents/spellbook/content/maps/wiki
rituals = infrastructure/rituals
scripts = infrastructure/scripts

; ── Oracle settings ──────────────────────────────────────────
oracle_backend = ollama          ; ollama (default) or lmstudio
oracle_host = 127.0.0.1:11434   ; used by the ollama backend
oracle_model = granite4:3b       ; default model for all stages

; Optional per-stage model overrides (fall back to oracle_model if absent):
; tagger_model       = granite4:3b  ; used by tagger_llm.py
; zettel_model       = cogito:8b    ; used by zettelkasten_llm.py
; shelf_model = cogito:8b    ; used by shelf_absorber.py for folder summarisation
; query_tagger_model = granite4:3b  ; used by query_tagger_llm.py
; query_llm_model    = cogito:8b    ; used by query_llm.py
; query_model        = cogito:8b    ; fallback for all query-stage scripts
; query_max_results  = 20           ; max zettels returned by query pipeline

shelves = /home/yourname/Documents/spellbook/content/shelves

; ── [rituals] — named ritual shortcuts ──────────────────────
[rituals]
sleep = infrastructure/rituals/sleep.ritual
reset = infrastructure/rituals/reset.ritual
query = infrastructure/rituals/query.ritual
query-cited = infrastructure/rituals/query-cited.ritual
wiki = infrastructure/rituals/wiki.ritual

; ── [tags] — your canonical tag vocabulary ──────────────────
[tags]
journal
todo
contacts
philosophy
; ... and so on

; ── [alias] — tag aliases ────────────────────────────────────
[alias]
contacts = people
tasks = todo

; ── [spellbook-ignored] — folders to exclude ─────────────────
[spellbook-ignored]
"infrastructure"
"projects"
```
*(Configuration block from)*

* **The [spellbook] Section:** This section defines where all of your important folders live. These paths are read by every script in the system. If you ever move your installation, updating these paths is all you need to do. The `oracle_backend` key selects which AI engine powers the oracle: `ollama` (the default) or `lmstudio`. The `oracle_host` and `oracle_model` settings provide connection details and the default model name. If you want different stages of the pipeline to use different models — a small, fast model for tagging and a larger model for final synthesis — you can configure per-stage overrides with keys like `tagger_model`, `zettel_model`, `shelf_model`, and `query_llm_model`. Each stage falls back to `oracle_model` if its specific key is absent.
* **The [rituals] Section:** This section registers rituals by name. When you run `spellbook sleep`, the system looks here for an entry named `sleep` and finds the path to its `.ritual` file. Registering a ritual here gives it a short, memorable name. Rituals can also be discovered automatically from the rituals/ directory without being listed here — more on that in Part IV.
* **The [tags] Section:** This section defines your approved vocabulary for tagging notes. The Oracle uses this list when deciding how to categorise your notes. You can add any tags you like — one per line. The system will not assign tags that aren't on this list, so this is how you keep your knowledge graph consistent.
* **The [alias] Section:** This section lets you define synonyms. If you write a note with the tag #people and you have an alias that maps people to contacts, the system will treat both as the same tag. This is useful when you want to support multiple spellings or concepts for the same category.
* **The [spellbook-ignored] Section:** This section lists folder names that Obsidian should treat as outside the knowledge graph. The `infrastructure/` folder is ignored by default because the scripts and rituals inside it are not notes — they are machinery. You would not want the Oracle trying to summarise them.

> ✦ **A Note on Paths:** Paths in `spellbook.conf` can be absolute (starting from the root of your drive, like `C:\Users\you\...` or `/home/you/...`) or relative (starting from the location of `spellbook.conf` itself, like `infrastructure/rituals`). The config reader resolves relative paths automatically, so either style works. When in doubt, use absolute paths — they are unambiguous.

---

## Part III — The Ritual Cycle
### How Information Flows
A ritual, in the folklore sense, is a set of actions performed in a prescribed order to achieve a specific effect. In the Spellbook, a ritual is precisely that — a sequence of steps that transform your notes from one state to another. The steps are always clear. The effects are always predictable.

The Spellbook has three primary rituals, which together form a cycle. Understanding this cycle is the key to understanding everything else.
* The **absorb** ritual takes a raw document from your inbox and converts it into a set of atomic, tagged notes. It is the ingestion step.
* The **focus** ritual reads all of your notes and rebuilds the tag index — the system of files that connects each tag to every note carrying it. It is the indexing step.
* The **sleep** ritual uses the tag index and the notes themselves to generate wiki pages — summary documents for each topic in your knowledge base. It is the synthesis step.

These three rituals are not automatic. You invoke them deliberately, when you choose. This is intentional: your knowledge base should grow on your schedule.

### Running a Ritual
Every ritual is invoked the same way, through the Spellbook's command-line interface. You open a terminal, navigate to your spellbook directory, and speak the name of the ritual.

To run a ritual, open your terminal application and type:
```bash
bb infrastructure/scripts/spellbook_cli.clj <ritual-name>
```
*(Command from)*

Replace `<ritual-name>` with the name of the ritual you want to run — for example, `absorb`, `focus`, or `sleep`. The `bb` at the beginning is the Babashka interpreter — the engine that runs the Spellbook's code.

To see all available rituals, run the same command with no ritual name, or with the word list:
```bash
bb infrastructure/scripts/spellbook_cli.clj
bb infrastructure/scripts/spellbook_cli.clj list
```
*(Commands from)*

> 🧙 **Tip from the Wizard:** If you find yourself typing this command often, you can create a short alias in your terminal. Ask someone comfortable with your operating system to help you set one up — it is a small effort that saves considerable typing over time.

### The Absorb Ritual
This is where the magic begins. You have a document — a journal entry, a web article you copied, a piece of research, a meeting note. Or perhaps a whole folder of materials from a project, an exported repository, a collection of references. You place it in your inbox. The absorb ritual picks it up, works out what kind of thing it is, and hands it to the appropriate handler. A pile of raw material becomes a set of ordered, tagged, connected thoughts.

**What absorb does, step by step:**
1. **Step 1:** `inbox_picker.py` selects a random item from your `inbox/`. This may be a file of any type, or an entire folder. Hidden files and dotfiles are skipped; everything else is a candidate.
2. **Step 2:** `dispatch.py` examines what was picked and routes it. This is the sorting office of the pipeline — it makes exactly one decision, and the rest of the pipeline never needs to know which path was taken. Every path produces the same thing: a JSON list of zettel text, ready for the next stage.
   * **If the item is a plain-text file** (`.txt`, `.md`, `.rst`, `.org`, and variants): `dispatch.py` calls `zettelkasten_llm.py`, which reads the file's contents and sends the full text to the Oracle — via `oracle_call.py`, which routes the request to your configured backend — with instructions to break it into atomic notes: one idea per note. The Oracle returns a list of self-contained statements. The original file is then moved to your `archive/` folder.
   * **If the item is a folder:** `dispatch.py` calls `shelf_absorber.py`, which moves the folder intact to `content/shelves/`, preserving its entire structure. The script reads the folder's file tree and any readable documents at the root level, then asks the Oracle to write a single anchor zettel summarising what the folder contains, its apparent purpose, and its key themes. The anchor zettel includes a link back to the shelf location so the folder is always traceable from your notes.
   * **If the item is any other file type** (audio, video, images, PDFs, documents, etc.): `dispatch.py` calls `unknown_absorber.py`, which moves the file to `assets/media/` (for audio, video, and images) or `assets/data/` (for everything else). The Oracle is given the filename and extension and asked to write a brief zettel recording the file's arrival and its new location. The file is preserved intact; the zettel serves as a record and a link. This is a holding pattern — to process these files properly, see the plugin system in `infrastructure/docs/PLUGINS.md`.
3. **Step 3:** `zettel_id_generator.py` assigns each note a unique identifier based on the current timestamp (formatted as YYYYMMDDHHMMSS). This is the Zettelkasten naming convention — each note's name is the moment it was created.
4. **Step 4:** `tagger_llm.py` sends each note to the oracle again, this time asking it to select appropriate tags from your canonical tag list. The tags are appended to the note, and the note is saved to `content/notes/`.

```bash
# absorb.ritual — the full pipeline
python3 infrastructure/scripts/inbox_picker.py \
| python3 infrastructure/scripts/dispatch.py \
| python3 infrastructure/scripts/zettel_id_generator.py \
| python3 infrastructure/scripts/tagger_llm.py
```
*(Pipeline from)*

Each `|` in a ritual is a pipe — it means "take the output of the previous step and pass it as the input to the next." This is how the Spellbook chains programs together without any one program needing to know about the others. The pipe is a fundamental concept in command-line computing, and the Spellbook uses it extensively.

> ✦ **The Zettelkasten Method:** The Zettelkasten (German: "note box") method was developed by sociologist Niklas Luhmann, who used it to write over 70 books. The principle is simple: one idea per note, each note identified by a unique ID, all notes linked by topic. The Spellbook automates the laborious parts of this method while preserving its core principle.

### The Focus Ritual
After many absorb sessions, your `notes/` folder will contain dozens or hundreds of atomic notes, each tagged with one or more topics. The focus ritual reads this entire collection and builds a map — a set of index files that answer the question: for each topic, which notes discuss it?

**What focus does, step by step:**
1. **Step 1:** `tag_hub_generator.py` reads the [tags] section of `spellbook.conf` and creates an empty index file for every tag in your canonical list. These files are named `tag-hub-{tagname}` and live in `content/maps/tag-hub/`. It also writes (or updates) a file called `canon-tags`, which is the authoritative list of known tags.
2. **Step 2:** `tag_hub_populator.py` walks through every file in `content/notes/` and scans for hashtag references (like #philosophy or #todo). For each tag it recognises from the `canon-tags` list, it adds that note's filename to the corresponding tag-hub file. Tags it does not recognise are recorded in a file called `non-canon-tags` — useful for discovering new tags your notes use that you haven't officially approved yet.

```bash
# focus.ritual — rebuild the tag index
python3 infrastructure/scripts/tag_hub_generator.py
python3 infrastructure/scripts/tag_hub_populator.py
```
*(Commands from)*

Run the focus ritual whenever you have added a significant number of new notes and want your tag index to reflect them. You do not need to run it after every single absorb — once every few sessions is fine.

### The Sleep Ritual
A wizard, after a long day of study, does not simply close their books. They reflect. They synthesise. They write summaries. The sleep ritual is the Spellbook doing this on your behalf, while you rest.

The sleep ritual calls `wiki_generator_llm.py`, which reads the tag index built by focus and produces a wiki page for each tag that has at least one note associated with it. The Oracle reads all notes tagged with a given topic, follows their source links back to the original archived documents, and synthesises a comprehensive, Obsidian-formatted summary page.

Existing wiki pages are not deleted — they are archived to `content/archive/wiki/` with a timestamp, so you never lose previous syntheses. The new wiki page takes their place in `content/maps/wiki/`.

The sleep ritual is the most computationally intensive of the three. It calls the Oracle multiple times — once per tag — and each call can take several minutes depending on your hardware and the size of your note collection. It is well named: run it before bed, and your wiki will be waiting for you in the morning.

### Other Rituals
Beyond the primary cycle, the Spellbook includes several supporting rituals for specific purposes.

* **consume:** The consume ritual is the absorb ritual run in a loop. It processes your inbox one file at a time, repeatedly, until every file has been absorbed and the inbox is empty. Useful after a long period of accumulation, when you want to process everything in one sitting without supervising each run.

* **wiki:** The wiki ritual runs `wiki_generator_llm.py` directly, allowing you to regenerate your wiki pages without going through the full sleep sequence. Run it when you want fresh summaries but have not added new notes.

* **query:** The query ritual accepts a natural-language question and searches your knowledge graph for relevant notes, using the Oracle to synthesise a readable prose answer. You can ask interactively (just run `query` with no arguments and it will prompt you), pass your question as trailing words on the command line, or pipe text in from another program. The `--no-wikis` flag excludes wiki pages from the search context; `--no-zettels` excludes individual notes.

  ```bash
  bb infrastructure/scripts/spellbook_cli.clj query what do I know about the Zettelkasten method
  bb infrastructure/scripts/spellbook_cli.clj query --no-wikis what did I write about Mersault
  echo "what is stoicism?" | bb infrastructure/scripts/spellbook_cli.clj query
  ```

  Behind the scenes, the query ritual is a seven-stage pipeline: `query_args_handler.py` parses your question and flags → `query_tagger_llm.py` asks the oracle to identify relevant tags → `wiki_retriever.py` loads matching wiki pages → `zettel_aggregator.py` gathers all notes associated with those tags → `query_ranker.py` scores and ranks them by relevance → `context_assembler.py` bundles the best material into a context block → `query_llm.py` sends it to the oracle and prints the answer.

* **query-cited:** Identical to query, but the answer includes a References section listing the specific Zettel notes and wiki pages that were used to construct it. Use this when you want to trace an answer back to its sources.

* **reset:** The reset ritual is, as its name suggests, a reset. It moves everything in your `archive/` back to your `inbox/` and wipes your processed notes and maps. This is useful when you want to reprocess your entire collection — perhaps after updating your tag list, or after upgrading the scripts. It is marked as destructive in the code comments for good reason: it deletes your processed notes. Your original documents are safely returned to the inbox, but make sure you understand what reset does before you invoke it.

* **install:** The install ritual re-runs the Install Wizard. This is useful if you want to set up Spellbook in a new location, or if you are helping someone else install it.

---

## Part IV — Crafting Your Own Rituals
### What Is a Ritual File?
You have now seen what rituals do. Let us look at what they are. A ritual file is, at its core, a list of instructions. Specifically, it is a plain text file — with the extension `.ritual` — where each non-blank, non-comment line is a command to be run in your terminal.

Here is the absorb ritual, in full:
```bash
# absorb.ritual
# Absorbs notes in the inbox and processes them
python3 infrastructure/scripts/inbox_picker.py | python3 infrastructure/scripts/dispatch.py | python3 infrastructure/scripts/zettel_id_generator.py | python3 infrastructure/scripts/tagger_llm.py
```
*(Code from)*

And here is the focus ritual:
```bash
# focus.ritual
# Rebuilds the tag-hub index.
python3 infrastructure/scripts/tag_hub_generator.py
python3 infrastructure/scripts/tag_hub_populator.py
```
*(Code from)*

Notice the difference. The absorb ritual is a single long pipeline — one line with the steps connected by pipes. The focus ritual is two separate lines. Both approaches are valid. Pipes connect steps that need to pass data to each other. Separate lines are used when each step operates independently.

The rules for ritual files are simple:
* Lines beginning with `#` are comments. They are ignored by the system.
* Blank lines are also ignored.
* Every other line is a command. The system runs them in order, from top to bottom.
* If a command fails (exits with an error), the ritual stops. The remaining steps do not run.
* Commands are run using the shell — so anything you can type into a terminal, you can put in a ritual.

### Your First Ritual — A Simple Example
Let us write a ritual together. We will make something small and safe — a ritual that prints a report of how many notes you have. Open a text editor. Create a new file. Type the following:

```bash
# count.ritual
# Counts the notes in your notes directory.
python3 -c "import os, subprocess; path = subprocess.run(['python3', 'infrastructure/scripts/config_reader.py', '-s', 'spellbook', '-k', 'notes'], capture_output=True, text=True).stdout.strip(); files = [f for f in os.listdir(path) if f.endswith('.md')]; print(f'You have {len(files)} notes in your Spellbook.')"
```
*(Code from)*

Save this file as `count.ritual` inside your `infrastructure/rituals/` folder. Then run it:
```bash
bb infrastructure/scripts/spellbook_cli.clj count
```
*(Command from)*

The system will find the ritual automatically because it lives in your `rituals/` directory. You do not need to register it in `spellbook.conf` unless you want to give it a different name.

### Registering a Ritual by Name
Any `.ritual` file placed in your `rituals/` directory is automatically available by its filename. If you name your file `count.ritual`, you invoke it as `count`. Simple. However, you can also register a ritual explicitly in `spellbook.conf`, under the `[rituals]` section. This lets you give it a different name, or point to a ritual file that lives somewhere else:

```ini
[rituals]
report = infrastructure/rituals/count.ritual
```
*(Config from)*

Now both `count` (from the filename) and `report` (from the config entry) invoke the same ritual. Entries in `[rituals]` take priority over file-based discovery when names conflict, which is useful if you want to override a default ritual with a customised version.

### Using the Utility Scripts
The Spellbook's scripts are designed to be reused. Three of them in particular — `config_reader.py`, `oracle_call.py`, and `ollama_call.py` — are utility scripts that your own rituals can call upon just as the built-in scripts do. They are the system's vocabulary; you are free to speak it.

**`config_reader.py` — reading your configuration**
This script reads a value from your `spellbook.conf` and prints it. It accepts a section name and a key name, and prints the corresponding value. Every built-in script uses it to find paths without hardcoding them.

```bash
# Get the path to your notes directory
python3 infrastructure/scripts/config_reader.py -s spellbook -k notes

# Get the path to your inbox
python3 infrastructure/scripts/config_reader.py -s spellbook -k inbox

# Get your configured oracle model name
python3 infrastructure/scripts/config_reader.py -s spellbook -k oracle_model
```
*(Commands from)*

Because it prints the result to the terminal, you can capture its output inside a ritual and use it in subsequent steps. This is the standard pattern:

```python
# In a ritual: use config_reader to get the notes path, then do something
python3 -c "
import subprocess
notes = subprocess.run(['python3', 'infrastructure/scripts/config_reader.py',
'-s', 'spellbook', '-k', 'notes'],
capture_output=True, text=True).stdout.strip()
print(notes)
"
```
*(Code from)*

**`oracle_call.py` — talking to the Oracle**
This is the script your rituals should call when they need to speak to the AI. It is a dispatcher: it reads `oracle_backend` from your `spellbook.conf` and forwards your request to either `ollama_call.py` or `call_lmstudio.py` — whichever backend you have configured. Its command-line interface is identical to both backends, so you can switch backends without changing any ritual or script that calls `oracle_call.py`.

```bash
# Ask the oracle a direct question (backend chosen automatically from conf)
python3 infrastructure/scripts/oracle_call.py \
-m granite4:3b \
-s "You are a helpful assistant." \
-u "What is the Zettelkasten method?"

# Pipe text into the oracle
echo "Summarise this note briefly." | python3 infrastructure/scripts/oracle_call.py \
-m granite4:3b \
-s "You are a summariser. Reply in one sentence."

# Request JSON output
python3 infrastructure/scripts/oracle_call.py \
-m granite4:3b -f json \
-s "Reply only with valid JSON." \
-u "List three colours as a JSON array."
```

All built-in AI-powered scripts (`zettelkasten_llm.py`, `tagger_llm.py`, `wiki_generator_llm.py`, `query_llm.py`, and the other query-pipeline scripts) call `oracle_call.py`, never the backend scripts directly. When you write your own rituals, follow the same convention.

**`ollama_call.py` and `call_lmstudio.py` — the backend scripts**
These scripts are the concrete implementations of the oracle interface. `ollama_call.py` speaks to an Ollama instance; `call_lmstudio.py` speaks to an LM Studio instance. Both accept the same arguments. You will rarely need to call them directly — `oracle_call.py` handles that — but they are available if you are testing a specific backend or building a ritual that should always use one engine regardless of your conf setting.

`call_lmstudio.py` connects to LM Studio's OpenAI-compatible API (default: `http://localhost:1234`). If your LM Studio instance is running on a different host or port, pass the `-H` flag.

Because these utility scripts are language-agnostic — they accept input, produce output, and communicate via standard terminal conventions — any command-line program in any language can use them. A ritual written in shell, in Python, in Ruby, or in anything else that can run a subprocess can call these scripts and use their output.

### A More Ambitious Ritual — Summarising a Note
Let us write something genuinely useful. A ritual that picks a random note from your collection and asks the Oracle to explain it in plain language.

```python
# explain.ritual
# Picks a random note and asks the oracle to explain it simply.
python3 -c "
import os, random, subprocess

# Ask config_reader where the notes folder is
notes_path = subprocess.run(
['python3', 'infrastructure/scripts/config_reader.py', '-s', 'spellbook', '-k', 'notes'],
capture_output=True, text=True).stdout.strip()

# Pick a random markdown file
files = [f for f in os.listdir(notes_path) if f.endswith('.md')]
chosen = os.path.join(notes_path, random.choice(files))
content = open(chosen).read()

# Ask the oracle to explain it (oracle_call.py routes to your configured backend)
result = subprocess.run(
['python3', 'infrastructure/scripts/oracle_call.py',
'-s', 'Explain this note in one paragraph. Use plain, simple language.',
'-u', content],
capture_output=True, text=True).stdout.strip()

print(f'Note: {os.path.basename(chosen)}')
print(result)
"
```
*(Code from)*

This ritual demonstrates the key pattern: call `config_reader` to find your paths, read your content, pass it to `oracle_call` for processing, and print the result. The ritual is self-contained — it does not modify any files and can be run as often as you like.

> ✦ **The Language-Agnostic Principle:** The Spellbook does not care what language your scripts are written in. Every script is just a command. If you can run it in a terminal, you can put it in a ritual. The built-in scripts happen to be written in Python, but a ritual can call a Ruby script, a Go binary, a shell script, or anything else your computer can execute. The pipeline is the architecture; the language is just a detail.

---

## Part VI — The Plugin System

*The grimoire you received is complete. The grimoire you will build is better.*

*Plugins are how you extend the Spellbook with your own pipeline steps, your own rituals, and your own AI backends — without touching the core scripts. They are the system's provision for the inevitable moment when you think: I wish it could also do this.*

The Spellbook's plugin system lives in `infrastructure/plugins/`. Each plugin is a subdirectory containing a `plugin.conf` file that identifies it to the system. At startup, the CLI scans this directory, reads every valid `plugin.conf` it finds, and registers each plugin's rituals and components alongside the built-in ones.

### What Plugins Can Do

A plugin can contribute two things:

**Rituals** — new named commands, discovered automatically, available through `spellbook list` and invocable the same way as any built-in ritual.

**Components** — named shortcuts for pipeline steps. Instead of writing the full path to a custom script every time you use it in a ritual, you write a short name like `pdf-reader.to_text`. The CLI expands this to the full invocation before passing the line to the shell.

Beyond new file-format handlers, plugins have been used for alternative oracle backends, pre-processing pipelines that clean input before it reaches the zettelkasten stage, post-processing rituals that export notes to other formats, and entirely independent workflows — journal rituals, review rituals, backup rituals — that have nothing to do with the absorb/focus/sleep cycle.

### Plugin Priority

The discovery process runs in three stages, from lowest to highest priority:

1. **Plugin rituals** — discovered from `infrastructure/plugins/`
2. **Rituals directory** — discovered from `infrastructure/rituals/`
3. **spellbook.conf [rituals] entries** — your conf is always the final word

This means you can always override a plugin's ritual by placing a same-named `.ritual` file in `infrastructure/rituals/`, and always override that with an explicit entry in your conf.

### A Minimal Plugin

A plugin requires exactly one file to be recognised by the system: `plugin.conf` at the root of its directory. Everything else is the plugin's own business.

```ini
; infrastructure/plugins/my-plugin/plugin.conf
[plugin]
name    = my-plugin
version = 1.0
rituals = rituals/

[components]
process = python3 scripts/my_script.py
```

With this in place, any `.ritual` files in `infrastructure/plugins/my-plugin/rituals/` become available as named rituals, and `my-plugin.process` becomes a valid component reference in any ritual file.

### Registering a Custom Absorber

Plugins can also intercept the absorb pipeline's routing stage. When `dispatch.py` picks up an item from the inbox, it checks `infrastructure/plugins/` before falling back to the built-in absorbers. If your plugin's `plugin.conf` declares a `[dispatch]` section, its handler will be called instead.

```ini
; infrastructure/plugins/my-plugin/plugin.conf
[plugin]
name    = my-plugin
version = 1.0

[dispatch]
handles_folders = scripts/my_folder_handler.py
handles_files   = scripts/my_file_handler.py
```

`handles_folders` replaces `shelf_absorber.py` for all folder-type inbox items. `handles_files` replaces `zettelkasten_llm.py` for all file-type inbox items. Either key may be omitted — if only one is declared, the built-in handler covers the other.

A custom absorber receives the item path on stdin and must write a JSON list of zettel strings to stdout — the same format `zettelkasten_llm.py` and `shelf_absorber.py` produce. The rest of the pipeline (`zettel_id_generator.py` and `tagger_llm.py`) does not know or care which absorber ran.

If multiple plugins declare handlers for the same key, the first one found in alphabetical order by plugin directory name takes priority. The built-in absorbers are always the last resort.

### Further Reading

The plugin system is documented in full in `infrastructure/docs/PLUGINS.md`. That document covers every `plugin.conf` key, the component registry and how expansion works, the optional sigil syntax for marking component references, collision handling when two plugins claim the same name, and a complete worked example building a PDF-ingestion plugin from scratch. If you are ready to build, start there.

---

## Part V — The Obsidian Vault

### Opening Your Vault
Obsidian is where you read and navigate everything the Spellbook has built. Think of it as the reading room of your library. The Spellbook is the library. Obsidian is the room where you sit with the books.

To connect Obsidian to your Spellbook, open Obsidian and choose **Open folder as vault**. Select your Spellbook installation directory — the root folder containing `spellbook.conf`. Obsidian will index all the Markdown files within it and present them as a connected knowledge base. You do not need to configure anything special in Obsidian. The Spellbook generates standard Markdown files with standard Obsidian-compatible link syntax. The base Obsidian installation — no plugins required — is all you need.

### Navigating Your Knowledge Graph
Your notes are connected by tags. Every note produced by the absorb ritual carries one or more hashtags. Obsidian recognises these and lets you search, filter, and navigate by them.

**The Tag Hub**
Inside `content/maps/tag-hub/` you will find a file named `tag-hub-{tagname}` for each of your canonical tags. Each file contains a list of every note that carries that tag. These files are not intended for reading directly — they are the raw index that the sleep ritual reads when generating wiki pages. But they are there if you want to inspect them.

Also in this folder is `canon-tags` — a single file listing all your approved tags — and `non-canon-tags` — a file listing tags found in your notes that are not in your canonical list. Review `non-canon-tags` periodically: it will reveal tags the Oracle has invented that you may want to officially adopt.

**The Wiki**
Inside `content/maps/wiki/` you will find one Markdown file per tag — a synthesised overview of everything your notes say about that topic. These are generated by the sleep ritual and updated each time you run it. Wiki pages include a References section at the bottom, listing the Zettel notes and original source files that were used to generate them. You can follow these links in Obsidian to trace any statement in a wiki back to its source.

**The Inbox and Archive**
Your `inbox/` folder is visible in Obsidian, but its files are transient — they will be absorbed and moved to `content/archive/`. The archive is the permanent home of your original documents, timestamped to prevent collisions.

### What Obsidian Shows You
Obsidian's graph view will display your notes as a network of connected nodes. Notes that share tags will appear close together. Wiki pages will appear as dense hubs connected to many notes. Your inbox documents, when they arrive, will appear as isolated nodes until they are absorbed and their Zettels are connected to the broader graph.

Using Obsidian's **tag search** (the Tags pane in the sidebar), you can browse all tags present in your vault and jump directly to any note carrying a given tag. This is the simplest way to navigate your knowledge base by topic.

> 🧙 **A Word of Advice:** Do not be alarmed by the `infrastructure/` folder appearing in your vault. It contains files Obsidian cannot do much with — `.clj`, `.py`, and `.ritual` files. The `[spellbook-ignored]` section in your config tells Obsidian to exclude these folders from its graph. If you see them appearing in unexpected places, check that your `.obsidian/app.json` or the excluded folders setting is configured correctly.

---

## Reference — spellbook.conf

**[spellbook] Section Keys**

| Key | Description |
| :--- | :--- |
| root | Absolute path to the Spellbook installation directory. |
| inbox | Path to the folder where raw input files are placed. |
| notes | Path to the folder where processed Zettel notes are stored. |
| archive | Path to the folder where original files are moved after processing. |
| shelves | Path to the folder where ingested folders are moved intact. Defaults to `{archive}/shelves/` if not set. |
| maps | Path to the `content/maps/` folder containing all generated map files. |
| taghub | Path to the `tag-hub/` subfolder inside `maps/`. Derived from maps if not set. |
| wiki | Path to the `wiki/` subfolder inside `maps/`. |
| hubs | Path to the `hubs/` subfolder inside `maps/`. |
| backlinks | Path to the `backlinks/` subfolder inside `maps/`. |
| journal | Path to the `journal/` folder for journal entries. |
| scripts | Path to the `infrastructure/scripts/` directory. |
| rituals | Path (absolute or relative) to the `infrastructure/rituals/` directory. |
| docs | Path to the `infrastructure/docs/` directory. |
| oracle_backend | Which AI backend to use: `ollama` (default) or `lmstudio`. |
| oracle_host | Host and port for the Ollama backend. Default: `127.0.0.1:11434`. |
| oracle_model | The default model name for all AI stages. Example: `granite4:3b`. |
| tagger_model | Model override for the tagging stage (`tagger_llm.py`). Falls back to `oracle_model`. |
| zettel_model | Model override for the zettelkasten stage (`zettelkasten_llm.py`). Falls back to `oracle_model`. |
| shelf_model | Model override for folder summarisation (`shelf_absorber.py`). Falls back to `oracle_model`. |
| query_model | Model override for all query-pipeline stages. Falls back to `oracle_model`. |
| query_tagger_model | Model override for query tag extraction (`query_tagger_llm.py`). Falls back to `query_model`. |
| query_llm_model | Model override for the final query answer step (`query_llm.py`). Falls back to `query_model`. |
| query_max_results | Maximum number of Zettels returned by `query_ranker.py`. Default: 20. |
| plugin_sigil | Optional character (e.g. `@`) that must prefix component references in ritual files. Leave empty (default) for no sigil. |

**[rituals] Section**
Each entry in `[rituals]` maps a short name to a ritual file path. Format: `name = path/to/file.ritual`. Paths may be relative to `spellbook.conf`'s location. Named rituals here override any `.ritual` file in the `rituals/` directory with the same name.

**[tags] Section**
Each non-blank, non-comment line in this section is a canonical tag name. Tags should be lowercase and use hyphens rather than spaces for multi-word tags (e.g. fine-arts, martial-arts). The `tag_hub_generator.py` script reads this section to build the initial tag index.

**[alias] Section**
Each entry maps one tag name to another. Format: `alias = canonical`. When a note uses the alias, the system treats it as the canonical tag. Useful for normalising spelling variations or synonyms.

**[commands] Section**
This section defines shorthand commands for common operations. For example, `journal = mv $filename content/journal` creates a command that moves a file to the journal directory. The `$filename` placeholder is replaced at runtime with the relevant file path.

**[spellbook-ignored] Section**
Each entry (in quotes) is a folder name that Obsidian should exclude from the vault's knowledge graph. Add any folder whose contents should not appear as notes — for example, `infrastructure/` and `projects/` are ignored by default.

---

## Reference — Ritual File Format
**File Format**
A ritual file is a plain text file with the `.ritual` extension. It must be placed in your `infrastructure/rituals/` directory to be automatically discoverable, or registered explicitly in the `[rituals]` section of `spellbook.conf`.

**Syntax Rules**

| Key | Description |
| :--- | :--- |
| # comment | Lines beginning with `#` are comments. They are ignored. |
| ; comment | Lines beginning with `;` are also comments. They are ignored. |
| blank line | Empty lines are ignored. |
| command | Any other line is a shell command, run in order from top to bottom. |
| cmd1 \| cmd2 | The pipe character connects two commands: the output of cmd1 becomes the input of cmd2. |

**Execution Context**
All commands in a ritual are run from the **working directory** — the folder containing `spellbook.conf`. This means paths like `infrastructure/scripts/` work correctly regardless of where you invoke the Spellbook command from.

**Error Handling**
If any command in a ritual returns a non-zero exit code (the conventional way for a program to signal that something went wrong), the ritual stops immediately. Subsequent commands are not run. This prevents a failed step from corrupting later steps.

**Invocation**
```bash
# Run a ritual by name
bb infrastructure/scripts/spellbook_cli.clj <ritual-name>

# List all available rituals
bb infrastructure/scripts/spellbook_cli.clj list
```
*(Commands from)*

---

## Glossary
The words below carry specific meaning within the Spellbook. Each carries both a metaphorical weight and a precise technical definition. Use this section when you encounter a word you are uncertain about.

* **Absorb:** The first ritual in the processing cycle. Takes a raw document or folder from the inbox, routes it through dispatch, breaks it into atomic notes via the Oracle, tags those notes, and saves them. Corresponds to the act of reading and processing new material. See also: **Consume** (the looping variant).
* **Absorber:** A script that receives inbox content on stdin and returns a JSON list of zettel strings on stdout. The built-in absorbers are `zettelkasten_llm.py` (for files) and `shelf_absorber.py` (for folders). Custom absorbers can be registered in a plugin's `plugin.conf` under the `[dispatch]` section.
* **Archive:** Both a verb (to archive: to move processed files into long-term storage) and a noun (the archive: the `content/archive/` folder where originals live after processing).
* **Atomic Note:** A note containing exactly one idea. The fundamental unit of the Zettelkasten method. Atomic notes are easier to link, tag, and retrieve than large composite documents.
* **Babashka (bb):** A portable Clojure interpreter. The runtime that executes the Spellbook's command-line interface. Babashka is a Lisp-family language runtime bundled as a single executable, which is why the Spellbook works across operating systems without additional setup.
* **Backend:** The AI engine that powers the Oracle. Currently supported: `ollama` and `lmstudio`. Selected via the `oracle_backend` key in `spellbook.conf`. The `oracle_call.py` dispatcher reads this setting and routes requests accordingly.
* **Canon Tags:** The approved list of tags defined in the `[tags]` section of `spellbook.conf`. The Oracle selects tags only from this list when processing notes.
* **Command:** A single instruction executed in a terminal. In a ritual file, each non-comment line is a command.
* **Component:** A named pipeline step registered by a plugin. Referenced in ritual files as `plugin-name.component-name`. The CLI expands it to a full shell invocation before passing the line to the shell.
* **Component Registry:** The internal lookup table the CLI builds at startup from all discovered plugin components. Maps short `plugin.component` keys to full shell invocations.
* **Config Reader:** The utility script `config_reader.py`. Accepts a section name and key name, reads `spellbook.conf`, and prints the corresponding value. Used by all built-in scripts to find their paths.
* **Consume:** A ritual that runs the full absorb pipeline in a loop until the inbox is empty — files and folders alike.
* **Dispatch:** The routing stage of the absorb pipeline. `dispatch.py` examines each inbox item, checks the plugin registry for a registered handler, and calls the appropriate absorber — `shelf_absorber.py` for folders, `zettelkasten_llm.py` for files. Its output is always a JSON list of zettel strings, regardless of which path was taken. Equivalent to invoking absorb repeatedly by hand. Useful for processing a large backlog in one go.
* **Focus:** The second ritual in the processing cycle. Reads all notes and rebuilds the tag index (tag-hub files). Corresponds to organising and indexing accumulated knowledge.
* **Grimoire:** Your Spellbook installation directory — the root folder containing `spellbook.conf` and all subdirectories.
* **Inbox:** The `inbox/` folder. The entry point for new material. Drop raw files here to be processed by the absorb ritual.
* **INI File:** A simple configuration file format. Sections are marked with `[names in brackets]`. Keys and values are separated by `=` signs. Comments begin with `;` or `#`. `spellbook.conf` is an INI file.
* **Non-Canon Tags:** Tags found in notes that are not on the approved canonical list. Recorded in the `non-canon-tags` file by the focus ritual. Reviewing this file is how you discover tags the Oracle has invented.
* **LM Studio:** An alternative local AI runtime. Like Ollama, it runs language models on your own machine and exposes an API the Spellbook can call. Enable it with `oracle_backend = lmstudio` in your conf.
* **Ollama:** A local AI runtime that downloads and runs language models on your own machine. The default oracle backend. Does not send your text to external servers.
* **Ollama Call:** The backend script `ollama_call.py`. Accepts a model name, a system prompt, and a user prompt, then calls Ollama and prints the response. Called by `oracle_call.py`; rarely invoked directly.
* **Oracle:** The AI layer of the Spellbook. Not a single program but an abstraction: `oracle_call.py` dispatches every AI request to whichever backend you have configured. Different models and different backends have different strengths — the Oracle is whichever combination you have set up.
* **Oracle Call:** The dispatcher script `oracle_call.py`. Reads `oracle_backend` from `spellbook.conf` and forwards every request to the appropriate backend script. This is what all built-in AI-powered scripts call. Your own rituals should do the same.
* **Pipeline:** A sequence of commands connected by pipes, where each command's output becomes the next command's input. The absorb ritual is a four-step pipeline; the query ritual is a seven-step pipeline.
* **Plugin:** A self-contained extension to the Spellbook, living in `infrastructure/plugins/`, identified by the presence of a `plugin.conf` file. A plugin may contribute rituals, pipeline components, or both. See `infrastructure/docs/PLUGINS.md` for the full specification.
* **plugin.conf:** The INI-format configuration file that identifies a directory as a Spellbook plugin and declares its rituals directory and component invocations. The only required structural element for a valid plugin.
* **Pipe:** The `|` character. Connects two commands so that the output of the left command becomes the input of the right command.
* **Ritual:** A plain text file (extension `.ritual`) containing a sequence of shell commands to be run in order. The fundamental unit of automation in the Spellbook.
* **Script:** A file containing code in any programming language. Scripts perform specific, reusable tasks. They can be called from rituals, from other scripts, or directly from the terminal.
* **Shell:** The program that interprets terminal commands. On Mac and Linux, this is typically Bash or Zsh. On Windows, it may be Command Prompt or PowerShell. Ritual commands are run through the shell.
* **Query:** A ritual that accepts a natural-language question and searches your knowledge graph to produce a prose answer.
* **Shelf:** A folder that has been ingested by the absorb ritual and moved intact to `content/shelves/`. Its internal structure is fully preserved. An anchor zettel, generated by the Oracle, is written to `content/notes/` and links back to the shelf location — so the folder is always traceable from your knowledge graph. A seven-stage pipeline. The `query-cited` variant appends a references section to the answer.
* **Sigil:** An optional prefix character (e.g. `@`) configured via `plugin_sigil` in `spellbook.conf`. When set, only tokens beginning with the sigil are treated as component references in ritual files. Useful when rituals grow complex and you want component references to stand out visually.
* **Sleep:** The third ritual in the processing cycle. Uses the tag index to generate wiki pages from notes. Corresponds to the synthesis and summarisation of accumulated knowledge. The `wiki` ritual is a standalone alias for this step.
* **spellbook.conf:** The configuration file at the root of your installation. Defines all paths, settings, tags, and ritual registrations. An INI-formatted text file.
* **Tag:** A hashtag within a note (e.g. `#philosophy`, `#todo`) that associates it with a topic. Tags are how the Spellbook connects notes to each other and to wiki pages.
* **Tag Hub:** A generated index file (`tag-hub-{tagname}`) listing every note associated with a given tag. Lives in `content/maps/tag-hub/`.
* **Vault:** Obsidian's term for a folder of Markdown files treated as a knowledge base. Point Obsidian at your Spellbook installation directory to open your vault.
* **Wiki:** A generated summary document for a topic, written by the Oracle from all notes associated with a given tag. Lives in `content/maps/wiki/`.
* **Working Directory:** The folder from which a command is run. All ritual commands execute from the directory containing `spellbook.conf`.
* **Zettel:** German for 'slip of paper.' An atomic note in the Zettelkasten tradition. In the Spellbook, Zettels are identified by a 14-digit timestamp (YYYYMMDDHHMMSS) as their filename.
* **Zettelkasten:** German for 'note box.' A note-taking method based on atomic, interlinked notes. Developed by Niklas Luhmann. The Spellbook's note structure is inspired by this method.

✦
You have reached the end of the manual. The grimoire is yours now.
Fill it well.
