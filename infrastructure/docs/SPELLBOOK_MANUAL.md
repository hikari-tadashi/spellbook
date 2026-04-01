# [cite_start]✦ THE SPELLBOOK ✦ [cite: 1]
[cite_start]**A Field Manual for the Apprentice Archivist** [cite: 2]
[cite_start]───────────────────────────── [cite: 3]
[cite_start]*Narrated by the Install Wizard* [cite: 4] [cite_start]*whose robes are singed, whose patience is vast,* [cite: 5] [cite_start]*and whose chief concern is that you succeed.* [cite: 6]

## [cite_start]A Note from Your Wizard [cite: 7]
Ah. You've opened the manual. Good. [cite_start]That already puts you ahead of most apprentices, who prefer to learn by setting things on fire. [cite: 8] I am the Install Wizard. [cite_start]You may have met me briefly when you first ran the Spellbook installer — I was the one asking you where you wanted your library and which oracle you preferred. [cite: 9] [cite_start]I am, in the tradition of wizards everywhere, both a guide and a piece of software. [cite: 10]

[cite_start]This manual will teach you how the Spellbook works, what all its peculiar pieces do, and — when you're ready — how to extend it with your own rituals. [cite: 11] Nothing here will be forced on you. [cite_start]Each section offers understanding first, and action only when you want it. [cite: 12] If you are new to software and feel uncertain: good. [cite_start]Uncertainty means you're paying attention. [cite: 13] [cite_start]I'll explain everything, and I'll never assume you know something I haven't taught you yet. [cite: 14] Now. [cite_start]Let us begin. [cite: 15]

This document is divided into five parts:
* [cite_start]**Part I** explains what the Spellbook is and why it works the way it does. [cite: 16]
* [cite_start]**Part II** covers the physical structure — the files and folders. [cite: 17]
* [cite_start]**Part III** walks through the ritual cycle, which is the heart of the system. [cite: 18]
* [cite_start]**Part IV** teaches you how to write your own rituals. [cite: 19]
* [cite_start]**Part V** covers your Obsidian vault — the interface where your knowledge lives. [cite: 20]

[cite_start]A reference section and glossary follow at the end. [cite: 21] You do not need to read this linearly. [cite_start]It is a reference as much as it is a guide. [cite: 22] [cite_start]But if you are new, Parts I and II are worth reading in order. [cite: 23]

---

## [cite_start]Part I — The World of the Spellbook [cite: 24]
### [cite_start]What Is the Spellbook? [cite: 25]
[cite_start]A spellbook, in folklore, is not merely a book of spells. [cite: 26] It is a personal record of a practitioner's accumulated knowledge — observations, experiments, correspondences, sources. [cite_start]It is a living document. [cite: 27] [cite_start]The spellbook grows with the wizard. [cite: 28]

The Spellbook is a personal knowledge management system. [cite_start]That is a formal way of saying it is a place where you put things you want to remember, and software that helps you organise, connect, and retrieve them. [cite: 29] [cite_start]You drop a document, a note, or a piece of writing into your inbox. [cite: 30] [cite_start]The Spellbook reads it, breaks it into focused ideas, tags those ideas, and files them. [cite: 31] [cite_start]Over time, it builds an interconnected web of knowledge — a graph of everything you've fed it, linked by topic. [cite: 32]

[cite_start]The system is designed to run locally, on your own computer. [cite: 33] [cite_start]Your notes never leave your machine unless you choose to put them somewhere. [cite: 34] [cite_start]The artificial intelligence it uses — which handles the reading, organising, and writing — runs locally too, through a piece of software called Ollama. [cite: 35]

[cite_start]The Spellbook is used through **Obsidian**, a free note-taking application that reads a folder of text files and displays them as an interconnected knowledge base. [cite: 36] Obsidian is the lens through which you read and navigate your Spellbook. [cite_start]The Spellbook's scripts produce the files; [cite: 37] [cite_start]Obsidian displays them. [cite: 38]

### [cite_start]The Language of the Spellbook [cite: 39]
Every craft has its vocabulary. [cite_start]A carpenter speaks of joinery; a physician speaks of anatomy. [cite: 40] [cite_start]The Spellbook's vocabulary borrows from the language of magic — not to be whimsical for its own sake, but because these metaphors map cleanly onto the underlying concepts. [cite: 41] [cite_start]Once you understand the map, both the folklore and the software become easier to navigate at once. [cite: 42]

[cite_start]The table below shows the Spellbook's terms alongside their plain-language meanings and their precise technical definitions. [cite: 43] [cite_start]When you encounter an unfamiliar word in this manual, return here. [cite: 44]

| Spellbook Term | In Plain English | What It Actually Is |
| :--- | :--- | :--- |
| Spellbook | Your knowledge base | [cite_start]The entire system: software, files, and configuration together [cite: 45] |
| Grimoire | Your personal library | [cite_start]Your installation directory — the folder containing everything [cite: 45] |
| Ritual | An automated task | [cite_start]A plain text file listing shell commands to run in sequence [cite: 45] |
| Script | A helper program | [cite_start]A file containing code (Python, Clojure, or any language) that does one specific job [cite: 45] |
| Spell | A command you cast | [cite_start]A single command line executed during a ritual [cite: 45] |
| Inbox | Your input tray | [cite_start]A folder where you drop raw notes and documents to be processed [cite: 45] |
| Zettel | An atomic idea | [cite_start]A single, self-contained note — one idea per note [cite: 45] |
| Tag Hub | A topic index | [cite_start]A generated file listing every note connected to a given tag [cite: 45] |
| Wiki | A topic summary | [cite_start]An AI-generated overview of a topic, drawn from all your notes on it [cite: 45] |
| Oracle | Your AI assistant | [cite_start]Ollama — the local AI that reads and writes on your behalf [cite: 45] |
| Model | The oracle's knowledge | [cite_start]The specific AI language model loaded into Ollama [cite: 45] |
| Configuration Tome | Your settings file | [cite_start]`spellbook.conf` — an INI file that tells the system where everything lives [cite: 45] |
| Install Wizard | The setup guide | [cite_start]The installation script — and, by extension, this narrator [cite: 45] |
| Canon Tags | Your approved vocabulary | [cite_start]A list of tags the system recognises as valid for categorisation [cite: 45] |
| Archive | Processed storage | [cite_start]A folder where original files are moved after being processed [cite: 45] |
| Pipeline | A chain of steps | [cite_start]A sequence of programs where each one's output feeds the next's input [cite: 45] |

### [cite_start]The Architecture at a Glance [cite: 46]
[cite_start]Before we descend into the details, let me show you the whole shape of the thing. [cite: 47] [cite_start]A map is worth ten descriptions of individual roads. [cite: 48]

[cite_start]The Spellbook's architecture has three layers, each built on top of the previous one. [cite: 49]
* [cite_start]**The first layer is the file system.** Your notes, your scripts, your rituals, your configuration — everything is a plain text file in a regular folder. [cite: 50] There is no database. There is no cloud service. [cite_start]If you can read a text file, you can see exactly what the Spellbook is doing. [cite: 51]
* [cite_start]**The second layer is the runtime.** This is the Babashka interpreter — a small, portable program that can read and execute Clojure code on any operating system. [cite: 52] [cite_start]Babashka is why the Spellbook works the same way on Windows, Mac, and Linux without modification. [cite: 53] [cite_start]Clojure is a dialect of Lisp, a family of programming languages known for their elegance. [cite: 54] [cite_start]You do not need to know Clojure to use the Spellbook. [cite: 55] [cite_start]You only need to know that Babashka is the engine that turns rituals into action. [cite: 56]
* [cite_start]**The third layer is the oracle.** This is Ollama, the local AI. [cite: 57] [cite_start]The Spellbook calls on Ollama to perform three tasks: breaking documents into atomic notes, assigning tags to those notes, and generating wiki pages from groups of notes. [cite: 58] Ollama runs on your machine. [cite_start]It does not send your text to the internet. [cite: 59]

[cite_start]The flow of information through the system looks like this: [cite: 60]

```text
  [ Your raw notes ]
        │
        ▼
  [ inbox/ folder ]   ← You drop files here
        │
        ▼  (absorb ritual)
  [ Oracle breaks text into Zettels ]
        │
        ▼  (Oracle assigns tags)
  [ content/notes/ ] ← Atomic, tagged notes
        │
        ▼  (focus ritual)
  [ content/maps/tag-hub/ ] ← Tag index built
        │
        ▼  (sleep ritual)
  [ content/maps/wiki/ ]  ← Wiki pages written
        │
        ▼
  [ Obsidian vault ]  ← You browse and read here
```
[cite_start]*(Diagram derived from [cite: 61])*

---

## [cite_start]Part II — The Grimoire [cite: 62]
### [cite_start]Your Directory Structure [cite: 63]
Every great library needs a consistent architecture. [cite_start]A book left in the wrong room is, for all practical purposes, lost. [cite: 64] [cite_start]The Spellbook's directory structure is not arbitrary — each folder has a single purpose, and understanding that purpose will help you navigate your installation confidently. [cite: 65]

[cite_start]When you installed the Spellbook, the Install Wizard created the following folder structure inside your chosen installation directory. [cite: 66] [cite_start]Here it is in full, with annotations: [cite: 67]

```text
spellbook/               ← Your grimoire root
├── inbox/               ← Drop raw notes here
├── content/
│   ├── notes/           ← Processed atomic notes (Zettels)
│   ├── archive/         ← Original files after processing
│   ├── assets/          ← Images and attachments
│   ├── journal/         ← Journal entries (moved here via command)
│   └── maps/            ← Generated knowledge maps
│       ├── tag-hub/     ← Tag index files
│       ├── wiki/        ← AI-generated wiki pages
│       ├── hubs/        ← Other hub files
│       └── backlinks/   ← Backlink index files
├── infrastructure/
│   ├── scripts/         ← The programs that run the system
│   ├── rituals/         ← The ritual files you invoke
│   └── documentation/   ← This manual lives here
├── projects/            ← Project-specific notes (optional)
└── spellbook.conf       ← Your configuration tome
```
[cite_start]*(Structure defined in [cite: 68])*

[cite_start]The most important thing to understand is the distinction between `content/` and `infrastructure/`. [cite: 69]
* [cite_start]Everything in `content/` is yours — your notes, your knowledge, your archive. [cite: 70]
* Everything in `infrastructure/` is the machinery of the system. [cite_start]You will read from infrastructure; [cite: 71] [cite_start]the system writes to content. [cite: 72]

The `inbox/` folder is the entry point. [cite_start]It stands apart at the root level because it is the one folder you interact with directly, every day. [cite: 73] [cite_start]Drop a file in. The system handles the rest. [cite: 74]

### [cite_start]The Configuration Tome — spellbook.conf [cite: 75]
[cite_start]In a real grimoire, the first pages describe the practitioner's particulars — their location, their preferred materials, their allegiances. [cite: 76] The Spellbook's configuration file serves the same purpose. [cite_start]It tells every part of the system where things are and how you prefer to work. [cite: 77]

[cite_start]The file `spellbook.conf` lives at the root of your installation. [cite: 78] [cite_start]It is a plain text file, readable in any text editor. [cite: 79] [cite_start]It is divided into sections, each marked with a name in square brackets. [cite: 80] Within each section, settings are written as `key = value` pairs. [cite_start]Lines beginning with `;` [cite: 81] [cite_start]or `#` are comments — notes to yourself that the system ignores. [cite: 82]

[cite_start]Here is what a typical `spellbook.conf` looks like, with explanations of each section: [cite: 83]

```ini
; ── [spellbook] — core paths ──────────────────────────────
[spellbook]
root          = /home/yourname/Documents/spellbook
inbox         = /home/yourname/Documents/spellbook/inbox
notes         = /home/yourname/Documents/spellbook/content/notes
archive       = /home/yourname/Documents/spellbook/content/archive
maps          = /home/yourname/Documents/spellbook/content/maps
taghub        = /home/yourname/Documents/spellbook/content/maps/tag-hub
wiki          = /home/yourname/Documents/spellbook/content/maps/wiki
rituals       = infrastructure/rituals
scripts       = infrastructure/scripts
ollama_host   = 127.0.0.1:11434
ollama_model  = granite4:3b

; ── [rituals] — named ritual shortcuts ──────────────────────
[rituals]
sleep         = infrastructure/rituals/sleep.ritual
reset         = infrastructure/rituals/reset.ritual
query         = infrastructure/rituals/query.ritual
wiki          = infrastructure/rituals/wiki.ritual

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
tasks    = todo

; ── [spellbook-ignored] — folders to exclude ─────────────────
[spellbook-ignored]
"infrastructure"
"projects"
```
[cite_start]*(Configuration block from [cite: 84])*

* [cite_start]**The [spellbook] Section:** [cite: 85] This section defines where all of your important folders live. [cite_start]These paths are read by every script in the system. [cite: 86] [cite_start]If you ever move your installation, updating these paths is all you need to do. [cite: 87] [cite_start]The `ollama_host` and `ollama_model` settings tell the system how to reach Ollama and which AI model to use. [cite: 88] [cite_start]If Ollama is running on your local machine, the host will be `127.0.0.1:11434`. [cite: 89] [cite_start]If it runs on another machine on your network, replace this with that machine's IP address and port. [cite: 90]
* [cite_start]**The [rituals] Section:** [cite: 91] This section registers rituals by name. [cite_start]When you run `spellbook sleep`, the system looks here for an entry named `sleep` and finds the path to its `.ritual` file. [cite: 92] [cite_start]Registering a ritual here gives it a short, memorable name. [cite: 93] [cite_start]Rituals can also be discovered automatically from the rituals/ directory without being listed here — more on that in Part IV. [cite: 94]
* [cite_start]**The [tags] Section:** [cite: 95] This section defines your approved vocabulary for tagging notes. [cite_start]The Oracle uses this list when deciding how to categorise your notes. [cite: 96] [cite_start]You can add any tags you like — one per line. [cite: 97] [cite_start]The system will not assign tags that aren't on this list, so this is how you keep your knowledge graph consistent. [cite: 98]
* [cite_start]**The [alias] Section:** [cite: 99] This section lets you define synonyms. [cite_start]If you write a note with the tag #people and you have an alias that maps people to contacts, the system will treat both as the same tag. [cite: 100] [cite_start]This is useful when you want to support multiple spellings or concepts for the same category. [cite: 101]
* [cite_start]**The [spellbook-ignored] Section:** [cite: 102] [cite_start]This section lists folder names that Obsidian should treat as outside the knowledge graph. [cite: 103] [cite_start]The `infrastructure/` folder is ignored by default because the scripts and rituals inside it are not notes — they are machinery. [cite: 104] [cite_start]You would not want the Oracle trying to summarise them. [cite: 105]

> ✦ **A Note on Paths:** Paths in `spellbook.conf` can be absolute (starting from the root of your drive, like `C:\Users\you\...` or `/home/you/...`) or relative (starting from the location of `spellbook.conf` itself, like `infrastructure/rituals`). The config reader resolves relative paths automatically, so either style works. [cite_start]When in doubt, use absolute paths — they are unambiguous. [cite: 106]

---

## [cite_start]Part III — The Ritual Cycle [cite: 107]
### [cite_start]How Information Flows [cite: 108]
[cite_start]A ritual, in the folklore sense, is a set of actions performed in a prescribed order to achieve a specific effect. [cite: 109] [cite_start]In the Spellbook, a ritual is precisely that — a sequence of steps that transform your notes from one state to another. [cite: 110] The steps are always clear. [cite_start]The effects are always predictable. [cite: 111]

[cite_start]The Spellbook has three primary rituals, which together form a cycle. [cite: 112] [cite_start]Understanding this cycle is the key to understanding everything else. [cite: 113]
* [cite_start]The **absorb** ritual takes a raw document from your inbox and converts it into a set of atomic, tagged notes. [cite: 114] [cite_start]It is the ingestion step. [cite: 115]
* [cite_start]The **focus** ritual reads all of your notes and rebuilds the tag index — the system of files that connects each tag to every note carrying it. [cite: 116] [cite_start]It is the indexing step. [cite: 117]
* [cite_start]The **sleep** ritual uses the tag index and the notes themselves to generate wiki pages — summary documents for each topic in your knowledge base. [cite: 118] [cite_start]It is the synthesis step. [cite: 119]

These three rituals are not automatic. [cite_start]You invoke them deliberately, when you choose. [cite: 120] [cite_start]This is intentional: your knowledge base should grow on your schedule. [cite: 121]

### [cite_start]Running a Ritual [cite: 122]
[cite_start]Every ritual is invoked the same way, through the Spellbook's command-line interface. [cite: 123] [cite_start]You open a terminal, navigate to your spellbook directory, and speak the name of the ritual. [cite: 124]

[cite_start]To run a ritual, open your terminal application and type: [cite: 125]
```bash
bb infrastructure/scripts/spellbook_cli.clj <ritual-name>
```
[cite_start]*(Command from [cite: 126])*

[cite_start]Replace `<ritual-name>` with the name of the ritual you want to run — for example, `absorb`, `focus`, or `sleep`. [cite: 127] [cite_start]The `bb` at the beginning is the Babashka interpreter — the engine that runs the Spellbook's code. [cite: 128]

[cite_start]To see all available rituals, run the same command with no ritual name, or with the word list: [cite: 129]
```bash
bb infrastructure/scripts/spellbook_cli.clj
bb infrastructure/scripts/spellbook_cli.clj list
```
[cite_start]*(Commands from [cite: 130])*

> 🧙 **Tip from the Wizard:** If you find yourself typing this command often, you can create a short alias in your terminal. [cite_start]Ask someone comfortable with your operating system to help you set one up — it is a small effort that saves considerable typing over time. [cite: 131]

### [cite_start]The Absorb Ritual [cite: 132]
This is where the magic begins. [cite_start]You have a document — a journal entry, a web article you copied, a piece of research, a meeting note. [cite: 133] You place it in your inbox. [cite_start]The absorb ritual picks it up, hands it to the Oracle, and watches as a pile of raw text becomes a set of ordered, tagged, connected thoughts. [cite: 134]

[cite_start]**What absorb does, step by step:** [cite: 135]
1.  [cite_start]**Step 1:** `inbox_picker.py` selects a random file from your `inbox/`. [cite: 136] [cite_start]This script reads `spellbook.conf` to find the inbox path, then picks one file at random. [cite: 137] [cite_start]Only .md (Markdown) and .txt files are selected. [cite: 138]
2.  [cite_start]**Step 2:** `zettelkasten_llm.py` receives the file path and reads its contents. [cite: 139] [cite_start]It sends the full text to Ollama with instructions to break it into atomic notes — one idea per note. [cite: 140] The Oracle returns a list of self-contained statements. [cite_start]The original file is then moved to your `archive/` folder. [cite: 141]
3.  [cite_start]**Step 3:** `zettel_id_generator.py` assigns each atomic note a unique identifier based on the current timestamp (formatted as YYYYMMDDHHMMSS). [cite: 142] [cite_start]This is the Zettelkasten naming convention — each note's name is the moment it was created. [cite: 143]
4.  [cite_start]**Step 4:** `tagger_llm.py` sends each note to Ollama again, this time asking it to select appropriate tags from your canonical tag list. [cite: 144] [cite_start]The tags are appended to the note, and the note is saved to `content/notes/`. [cite: 145]

```bash
# absorb.ritual — the full pipeline
python3 infrastructure/scripts/inbox_picker.py \
    | python3 infrastructure/scripts/zettelkasten_llm.py \
    | python3 infrastructure/scripts/zettel_id_generator.py \
    | python3 infrastructure/scripts/tagger_llm.py
```
[cite_start]*(Pipeline from [cite: 146])*

[cite_start]Each `|` in a ritual is a pipe — it means "take the output of the previous step and pass it as the input to the next." [cite: 147] [cite_start]This is how the Spellbook chains programs together without any one program needing to know about the others. [cite: 148] [cite_start]The pipe is a fundamental concept in command-line computing, and the Spellbook uses it extensively. [cite: 149]

> ✦ **The Zettelkasten Method:** The Zettelkasten (German: "note box") method was developed by sociologist Niklas Luhmann, who used it to write over 70 books. The principle is simple: one idea per note, each note identified by a unique ID, all notes linked by topic. [cite_start]The Spellbook automates the laborious parts of this method while preserving its core principle. [cite: 150]

### [cite_start]The Focus Ritual [cite: 151]
[cite_start]After many absorb sessions, your `notes/` folder will contain dozens or hundreds of atomic notes, each tagged with one or more topics. [cite: 152] [cite_start]The focus ritual reads this entire collection and builds a map — a set of index files that answer the question: for each topic, which notes discuss it? [cite: 153]

[cite_start]**What focus does, step by step:** [cite: 154]
1.  [cite_start]**Step 1:** `tag_hub_generator.py` reads the [tags] section of `spellbook.conf` and creates an empty index file for every tag in your canonical list. [cite: 155] These files are named `tag-hub-{tagname}` and live in `content/maps/tag-hub/`. [cite_start]It also writes (or updates) a file called `canon-tags`, which is the authoritative list of known tags. [cite: 156]
2.  [cite_start]**Step 2:** `tag_hub_populator.py` walks through every file in `content/notes/` and scans for hashtag references (like #philosophy or #todo). [cite: 157] [cite_start]For each tag it recognises from the `canon-tags` list, it adds that note's filename to the corresponding tag-hub file. [cite: 158] [cite_start]Tags it does not recognise are recorded in a file called `non-canon-tags` — useful for discovering new tags your notes use that you haven't officially approved yet. [cite: 159]

```bash
# focus.ritual — rebuild the tag index
python3 infrastructure/scripts/tag_hub_generator.py
python3 infrastructure/scripts/tag_hub_populator.py
```
[cite_start]*(Commands from [cite: 160])*

[cite_start]Run the focus ritual whenever you have added a significant number of new notes and want your tag index to reflect them. [cite: 161] [cite_start]You do not need to run it after every single absorb — once every few sessions is fine. [cite: 162]

### [cite_start]The Sleep Ritual [cite: 163]
A wizard, after a long day of study, does not simply close their books. They reflect. [cite_start]They synthesise. [cite: 164] They write summaries. [cite_start]The sleep ritual is the Spellbook doing this on your behalf, while you rest. [cite: 165]

[cite_start]The sleep ritual calls `wiki_generator_llm.py`, which reads the tag index built by focus and produces a wiki page for each tag that has at least one note associated with it. [cite: 166] [cite_start]The Oracle reads all notes tagged with a given topic, follows their source links back to the original archived documents, and synthesises a comprehensive, Obsidian-formatted summary page. [cite: 167]

[cite_start]Existing wiki pages are not deleted — they are archived to `content/archive/wiki/` with a timestamp, so you never lose previous syntheses. [cite: 168] [cite_start]The new wiki page takes their place in `content/maps/wiki/`. [cite: 169]

[cite_start]The sleep ritual is the most computationally intensive of the three. [cite: 170] [cite_start]It calls the Oracle multiple times — once per tag — and each call can take several minutes depending on your hardware and the size of your note collection. [cite: 171] [cite_start]It is well named: run it before bed, and your wiki will be waiting for you in the morning. [cite: 172]

### [cite_start]Other Rituals [cite: 173]
[cite_start]Beyond the primary cycle, the Spellbook includes several supporting rituals for specific purposes. [cite: 174]
* [cite_start]**reset:** [cite: 175] [cite_start]The reset ritual is, as its name suggests, a reset. [cite: 176] [cite_start]It moves everything in your `archive/` back to your `inbox/` and wipes your processed notes and maps. [cite: 177] [cite_start]This is useful when you want to reprocess your entire collection — perhaps after updating your tag list, or after upgrading the scripts. [cite: 178] [cite_start]It is marked as destructive in the code comments for good reason: it deletes your processed notes. [cite: 179] [cite_start]Your original documents are safely returned to the inbox, but make sure you understand what reset does before you invoke it. [cite: 180]
* [cite_start]**wiki:** [cite: 181] [cite_start]The wiki ritual is an alias for the sleep ritual's wiki generation step. [cite: 182] [cite_start]It runs `wiki_generator_llm.py` directly, allowing you to regenerate your wiki without running the full sleep sequence. [cite: 183] [cite_start]This is useful when you want fresh wiki pages but have not added new notes. [cite: 184]
* [cite_start]**query:** [cite: 185] The query ritual is planned but not yet implemented. [cite_start]When complete, it will accept a natural-language question and search your knowledge graph for relevant notes, using the Oracle to rank and present the results. [cite: 186] [cite_start]The ritual file currently prints a message acknowledging this. [cite: 187]
* [cite_start]**install:** [cite: 188] The install ritual re-runs the Install Wizard. [cite_start]This is useful if you want to set up Spellbook in a new location, or if you are helping someone else install it. [cite: 189]

---

## [cite_start]Part IV — Crafting Your Own Rituals [cite: 190]
### [cite_start]What Is a Ritual File? [cite: 191]
You have now seen what rituals do. [cite_start]Let us look at what they are. [cite: 192] [cite_start]A ritual file is, at its core, a list of instructions. [cite: 193] [cite_start]Specifically, it is a plain text file — with the extension `.ritual` — where each non-blank, non-comment line is a command to be run in your terminal. [cite: 194]

[cite_start]Here is the absorb ritual, in full: [cite: 195]
```bash
# absorb.ritual
# Absorbs notes in the inbox and processes them
python3 infrastructure/scripts/inbox_picker.py | python3 infrastructure/scripts/zettelkasten_llm.py | python3 infrastructure/scripts/zettel_id_generator.py | python3 infrastructure/scripts/tagger_llm.py
```
[cite_start]*(Code from [cite: 196])*

[cite_start]And here is the focus ritual: [cite: 197]
```bash
# focus.ritual
# Rebuilds the tag-hub index.
python3 infrastructure/scripts/tag_hub_generator.py
python3 infrastructure/scripts/tag_hub_populator.py
```
[cite_start]*(Code from [cite: 198])*

Notice the difference. [cite_start]The absorb ritual is a single long pipeline — one line with the steps connected by pipes. [cite: 199] The focus ritual is two separate lines. [cite_start]Both approaches are valid. [cite: 200] Pipes connect steps that need to pass data to each other. [cite_start]Separate lines are used when each step operates independently. [cite: 201]

[cite_start]The rules for ritual files are simple: [cite: 202]
* Lines beginning with `#` are comments. [cite_start]They are ignored by the system. [cite: 203]
* [cite_start]Blank lines are also ignored. [cite: 204]
* Every other line is a command. [cite_start]The system runs them in order, from top to bottom. [cite: 205]
* If a command fails (exits with an error), the ritual stops. [cite_start]The remaining steps do not run. [cite: 206]
* [cite_start]Commands are run using the shell — so anything you can type into a terminal, you can put in a ritual. [cite: 207]

### [cite_start]Your First Ritual — A Simple Example [cite: 208]
Let us write a ritual together. [cite_start]We will make something small and safe — a ritual that prints a report of how many notes you have. [cite: 209] Open a text editor. Create a new file. [cite_start]Type the following: [cite: 210]

```bash
# count.ritual
# Counts the notes in your notes directory.
python3 -c "import os, subprocess; path = subprocess.run(['python3', 'infrastructure/scripts/config_reader.py', '-s', 'spellbook', '-k', 'notes'], capture_output=True, text=True).stdout.strip(); files = [f for f in os.listdir(path) if f.endswith('.md')]; print(f'You have {len(files)} notes in your Spellbook.')"
```
[cite_start]*(Code from [cite: 211])*

Save this file as `count.ritual` inside your `infrastructure/rituals/` folder. [cite_start]Then run it: [cite: 212]
```bash
bb infrastructure/scripts/spellbook_cli.clj count
```
[cite_start]*(Command from [cite: 213])*

[cite_start]The system will find the ritual automatically because it lives in your `rituals/` directory. [cite: 214] [cite_start]You do not need to register it in `spellbook.conf` unless you want to give it a different name. [cite: 215]

### [cite_start]Registering a Ritual by Name [cite: 216]
[cite_start]Any `.ritual` file placed in your `rituals/` directory is automatically available by its filename. [cite: 217] If you name your file `count.ritual`, you invoke it as `count`. [cite_start]Simple. [cite: 218] [cite_start]However, you can also register a ritual explicitly in `spellbook.conf`, under the `[rituals]` section. [cite: 219] [cite_start]This lets you give it a different name, or point to a ritual file that lives somewhere else: [cite: 220]

```ini
[rituals]
report = infrastructure/rituals/count.ritual
```
[cite_start]*(Config from [cite: 221])*

[cite_start]Now both `count` (from the filename) and `report` (from the config entry) invoke the same ritual. [cite: 222] [cite_start]Entries in `[rituals]` take priority over file-based discovery when names conflict, which is useful if you want to override a default ritual with a customised version. [cite: 223]

### [cite_start]Using the Utility Scripts [cite: 224]
The Spellbook's scripts are designed to be reused. [cite_start]Two of them in particular — `config_reader.py` and `ollama_call.py` — are utility scripts that your own rituals can call upon just as the built-in scripts do. [cite: 225] [cite_start]They are the system's vocabulary; you are free to speak it. [cite: 226]

[cite_start]**`config_reader.py` — reading your configuration** [cite: 227]
[cite_start]This script reads a value from your `spellbook.conf` and prints it. [cite: 228] [cite_start]It accepts a section name and a key name, and prints the corresponding value. [cite: 229] [cite_start]Every built-in script uses it to find paths without hardcoding them. [cite: 230]

```bash
# Get the path to your notes directory
python3 infrastructure/scripts/config_reader.py -s spellbook -k notes

# Get the path to your inbox
python3 infrastructure/scripts/config_reader.py -s spellbook -k inbox

# Get your configured Ollama model name
python3 infrastructure/scripts/config_reader.py -s spellbook -k ollama_model
```
[cite_start]*(Commands from [cite: 231])*

[cite_start]Because it prints the result to the terminal, you can capture its output inside a ritual and use it in subsequent steps. [cite: 232] [cite_start]This is the standard pattern: [cite: 233]

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
[cite_start]*(Code from [cite: 234])*

[cite_start]**`ollama_call.py` — talking to the Oracle** [cite: 235]
[cite_start]This script sends a prompt to Ollama and prints the response. [cite: 236] [cite_start]It accepts a system prompt (instructions to the Oracle about its role) and a user prompt (your actual question or content). [cite: 237] [cite_start]You can pipe text into it, pass it via command-line argument, or combine both. [cite: 238]

```bash
# Ask the oracle a direct question
python3 infrastructure/scripts/ollama_call.py \
  -m granite4:3b \
  -s "You are a helpful assistant." \
  -u "What is the Zettelkasten method?"

# Pipe text into the oracle
echo "Summarise this note briefly." | python3 infrastructure/scripts/ollama_call.py \
  -m granite4:3b \
  -s "You are a summariser. Reply in one sentence."

# Request JSON output
python3 infrastructure/scripts/ollama_call.py \
  -m granite4:3b -f json \
  -s "Reply only with valid JSON." \
  -u "List three colours as a JSON array."
```
[cite_start]*(Commands from [cite: 239])*

[cite_start]Because these two scripts are language-agnostic utilities — they accept input, produce output, and communicate via standard terminal conventions — any command-line program in any language can use them. [cite: 240] [cite_start]A ritual written in shell, in Python, in Ruby, or in anything else that can run a subprocess can call these scripts and use their output. [cite: 241]

### [cite_start]A More Ambitious Ritual — Summarising a Note [cite: 242]
Let us write something genuinely useful. [cite_start]A ritual that picks a random note from your collection and asks the Oracle to explain it in plain language. [cite: 243]

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

# Ask the oracle to explain it
result = subprocess.run(
  ['python3', 'infrastructure/scripts/ollama_call.py',
   '-s', 'Explain this note in one paragraph. Use plain, simple language.',
   '-u', content],
  capture_output=True, text=True).stdout.strip()

print(f'Note: {os.path.basename(chosen)}')
print(result)
"
```
[cite_start]*(Code from [cite: 244])*

[cite_start]This ritual demonstrates the key pattern: call `config_reader` to find your paths, read your content, pass it to `ollama_call` for processing, and print the result. [cite: 245] [cite_start]The ritual is self-contained — it does not modify any files and can be run as often as you like. [cite: 246]

> ✦ **The Language-Agnostic Principle:** The Spellbook does not care what language your scripts are written in. Every script is just a command. If you can run it in a terminal, you can put it in a ritual. The built-in scripts happen to be written in Python, but a ritual can call a Ruby script, a Go binary, a shell script, or anything else your computer can execute. [cite_start]The pipeline is the architecture; the language is just a detail. [cite: 247]

---

## [cite_start]Part V — The Obsidian Vault [cite: 248]
### [cite_start]Opening Your Vault [cite: 249]
[cite_start]Obsidian is where you read and navigate everything the Spellbook has built. [cite: 250] Think of it as the reading room of your library. [cite_start]The Spellbook is the library. [cite: 251] [cite_start]Obsidian is the room where you sit with the books. [cite: 252]

[cite_start]To connect Obsidian to your Spellbook, open Obsidian and choose **Open folder as vault**. [cite: 253] [cite_start]Select your Spellbook installation directory — the root folder containing `spellbook.conf`. [cite: 254] [cite_start]Obsidian will index all the Markdown files within it and present them as a connected knowledge base. [cite: 255] [cite_start]You do not need to configure anything special in Obsidian. [cite: 256] [cite_start]The Spellbook generates standard Markdown files with standard Obsidian-compatible link syntax. [cite: 257] [cite_start]The base Obsidian installation — no plugins required — is all you need. [cite: 258]

### [cite_start]Navigating Your Knowledge Graph [cite: 259]
Your notes are connected by tags. [cite_start]Every note produced by the absorb ritual carries one or more hashtags. [cite: 260] [cite_start]Obsidian recognises these and lets you search, filter, and navigate by them. [cite: 261]

[cite_start]**The Tag Hub** [cite: 262]
[cite_start]Inside `content/maps/tag-hub/` you will find a file named `tag-hub-{tagname}` for each of your canonical tags. [cite: 263] [cite_start]Each file contains a list of every note that carries that tag. [cite: 264] [cite_start]These files are not intended for reading directly — they are the raw index that the sleep ritual reads when generating wiki pages. [cite: 265] [cite_start]But they are there if you want to inspect them. [cite: 266]

[cite_start]Also in this folder is `canon-tags` — a single file listing all your approved tags — and `non-canon-tags` — a file listing tags found in your notes that are not in your canonical list. [cite: 267] [cite_start]Review `non-canon-tags` periodically: it will reveal tags the Oracle has invented that you may want to officially adopt. [cite: 268]

[cite_start]**The Wiki** [cite: 269]
[cite_start]Inside `content/maps/wiki/` you will find one Markdown file per tag — a synthesised overview of everything your notes say about that topic. [cite: 270] [cite_start]These are generated by the sleep ritual and updated each time you run it. [cite: 271] [cite_start]Wiki pages include a References section at the bottom, listing the Zettel notes and original source files that were used to generate them. [cite: 272] [cite_start]You can follow these links in Obsidian to trace any statement in a wiki back to its source. [cite: 273]

[cite_start]**The Inbox and Archive** [cite: 274]
[cite_start]Your `inbox/` folder is visible in Obsidian, but its files are transient — they will be absorbed and moved to `content/archive/`. [cite: 275] [cite_start]The archive is the permanent home of your original documents, timestamped to prevent collisions. [cite: 276]

### [cite_start]What Obsidian Shows You [cite: 277]
[cite_start]Obsidian's graph view will display your notes as a network of connected nodes. [cite: 278] Notes that share tags will appear close together. [cite_start]Wiki pages will appear as dense hubs connected to many notes. [cite: 279] [cite_start]Your inbox documents, when they arrive, will appear as isolated nodes until they are absorbed and their Zettels are connected to the broader graph. [cite: 280]

[cite_start]Using Obsidian's **tag search** (the Tags pane in the sidebar), you can browse all tags present in your vault and jump directly to any note carrying a given tag. [cite: 281] [cite_start]This is the simplest way to navigate your knowledge base by topic. [cite: 282]

> 🧙 **A Word of Advice:** Do not be alarmed by the `infrastructure/` folder appearing in your vault. It contains files Obsidian cannot do much with — `.clj`, `.py`, and `.ritual` files. The `[spellbook-ignored]` section in your config tells Obsidian to exclude these folders from its graph. [cite_start]If you see them appearing in unexpected places, check that your `.obsidian/app.json` or the excluded folders setting is configured correctly. [cite: 283]

---

## [cite_start]Reference — spellbook.conf [cite: 284]

[cite_start]**[spellbook] Section Keys** [cite: 285]

| Key | Description |
| :--- | :--- |
| root | [cite_start]Absolute path to the Spellbook installation directory. [cite: 286] |
| inbox | [cite_start]Path to the folder where raw input files are placed. [cite: 286] |
| notes | [cite_start]Path to the folder where processed Zettel notes are stored. [cite: 286] |
| archive | [cite_start]Path to the folder where original files are moved after processing. [cite: 286] |
| maps | [cite_start]Path to the `content/maps/` folder containing all generated map files. [cite: 286] |
| taghub | Path to the `tag-hub/` subfolder inside `maps/`. [cite_start]Derived from maps if not set. [cite: 286] |
| wiki | [cite_start]Path to the `wiki/` subfolder inside `maps/`. [cite: 286] |
| hubs | [cite_start]Path to the `hubs/` subfolder inside `maps/`. [cite: 286] |
| backlinks | [cite_start]Path to the `backlinks/` subfolder inside `maps/`. [cite: 286] |
| journal | [cite_start]Path to the `journal/` folder for journal entries. [cite: 286] |
| scripts | [cite_start]Path to the `infrastructure/scripts/` directory. [cite: 286] |
| rituals | [cite_start]Path (absolute or relative) to the `infrastructure/rituals/` directory. [cite: 286] |
| documentation | [cite_start]Path to the `infrastructure/documentation/` directory. [cite: 286] |
| ollama_host | Host and port for Ollama. [cite_start]Default: `127.0.0.1:11434`. [cite: 286] |
| ollama_model | The default Ollama model name to use. [cite_start]Example: `granite4:3b` or `cogito:8b`. [cite: 286] |

[cite_start]**[rituals] Section** [cite: 287]
Each entry in `[rituals]` maps a short name to a ritual file path. [cite_start]Format: `name = path/to/file.ritual`. [cite: 288] Paths may be relative to `spellbook.conf`'s location. [cite_start]Named rituals here override any `.ritual` file in the `rituals/` directory with the same name. [cite: 289]

[cite_start]**[tags] Section** [cite: 290]
[cite_start]Each non-blank, non-comment line in this section is a canonical tag name. [cite: 291] [cite_start]Tags should be lowercase and use hyphens rather than spaces for multi-word tags (e.g. fine-arts, martial-arts). [cite: 292] [cite_start]The `tag_hub_generator.py` script reads this section to build the initial tag index. [cite: 293]

[cite_start]**[alias] Section** [cite: 294]
Each entry maps one tag name to another. [cite_start]Format: `alias = canonical`. [cite: 295] [cite_start]When a note uses the alias, the system treats it as the canonical tag. [cite: 296] [cite_start]Useful for normalising spelling variations or synonyms. [cite: 297]

[cite_start]**[commands] Section** [cite: 298]
This section defines shorthand commands for common operations. [cite_start]For example, `journal = mv $filename content/journal` creates a command that moves a file to the journal directory. [cite: 299] [cite_start]The `$filename` placeholder is replaced at runtime with the relevant file path. [cite: 300]

[cite_start]**[spellbook-ignored] Section** [cite: 301]
[cite_start]Each entry (in quotes) is a folder name that Obsidian should exclude from the vault's knowledge graph. [cite: 302] [cite_start]Add any folder whose contents should not appear as notes — for example, `infrastructure/` and `projects/` are ignored by default. [cite: 303]

---

## [cite_start]Reference — Ritual File Format [cite: 304]
[cite_start]**File Format** [cite: 305]
[cite_start]A ritual file is a plain text file with the `.ritual` extension. [cite: 306] [cite_start]It must be placed in your `infrastructure/rituals/` directory to be automatically discoverable, or registered explicitly in the `[rituals]` section of `spellbook.conf`. [cite: 307]

[cite_start]**Syntax Rules** [cite: 308]

| Key | Description |
| :--- | :--- |
| # comment | Lines beginning with `#` are comments. [cite_start]They are ignored. [cite: 309] |
| ; comment | Lines beginning with `;` are also comments. [cite_start]They are ignored. [cite: 309] |
| blank line | [cite_start]Empty lines are ignored. [cite: 309] |
| command | [cite_start]Any other line is a shell command, run in order from top to bottom. [cite: 309] |
| cmd1 \| cmd2 | [cite_start]The pipe character connects two commands: the output of cmd1 becomes the input of cmd2. [cite: 309] |

[cite_start]**Execution Context** [cite: 310]
[cite_start]All commands in a ritual are run from the **working directory** — the folder containing `spellbook.conf`. [cite: 311] [cite_start]This means paths like `infrastructure/scripts/` work correctly regardless of where you invoke the Spellbook command from. [cite: 312]

[cite_start]**Error Handling** [cite: 313]
[cite_start]If any command in a ritual returns a non-zero exit code (the conventional way for a program to signal that something went wrong), the ritual stops immediately. [cite: 314] Subsequent commands are not run. [cite_start]This prevents a failed step from corrupting later steps. [cite: 315]

[cite_start]**Invocation** [cite: 316]
```bash
# Run a ritual by name
bb infrastructure/scripts/spellbook_cli.clj <ritual-name>

# List all available rituals
bb infrastructure/scripts/spellbook_cli.clj list
```
[cite_start]*(Commands from [cite: 317])*

---

## [cite_start]Glossary [cite: 318]
The words below carry specific meaning within the Spellbook. [cite_start]Each carries both a metaphorical weight and a precise technical definition. [cite: 319] [cite_start]Use this section when you encounter a word you are uncertain about. [cite: 320]

* [cite_start]**Absorb:** [cite: 321] The first ritual in the processing cycle. [cite_start]Takes a raw document from the inbox, breaks it into atomic notes via the Oracle, tags those notes, and saves them. [cite: 322] [cite_start]Corresponds to the act of reading and processing new material. [cite: 323]
* [cite_start]**Archive:** [cite: 324] [cite_start]Both a verb (to archive: to move processed files into long-term storage) and a noun (the archive: the `content/archive/` folder where originals live after processing). [cite: 325]
* [cite_start]**Atomic Note:** [cite: 326] A note containing exactly one idea. [cite_start]The fundamental unit of the Zettelkasten method. [cite: 327] [cite_start]Atomic notes are easier to link, tag, and retrieve than large composite documents. [cite: 328]
* [cite_start]**Babashka (bb):** [cite: 329] A portable Clojure interpreter. [cite_start]The runtime that executes the Spellbook's command-line interface. [cite: 330] [cite_start]Babashka is a Lisp-family language runtime bundled as a single executable, which is why the Spellbook works across operating systems without additional setup. [cite: 331]
* [cite_start]**Canon Tags:** [cite: 332] [cite_start]The approved list of tags defined in the `[tags]` section of `spellbook.conf`. [cite: 333] [cite_start]The Oracle selects tags only from this list when processing notes. [cite: 334]
* [cite_start]**Command:** [cite: 335] A single instruction executed in a terminal. [cite_start]In a ritual file, each non-comment line is a command. [cite: 336]
* [cite_start]**Config Reader:** [cite: 337] The utility script `config_reader.py`. [cite_start]Accepts a section name and key name, reads `spellbook.conf`, and prints the corresponding value. [cite: 338] [cite_start]Used by all built-in scripts to find their paths. [cite: 339]
* [cite_start]**Focus:** [cite: 340] The second ritual in the processing cycle. [cite_start]Reads all notes and rebuilds the tag index (tag-hub files). [cite: 341] [cite_start]Corresponds to organising and indexing accumulated knowledge. [cite: 342]
* [cite_start]**Grimoire:** [cite: 343] [cite_start]Your Spellbook installation directory — the root folder containing `spellbook.conf` and all subdirectories. [cite: 344]
* [cite_start]**Inbox:** [cite: 345] The `inbox/` folder. The entry point for new material. [cite_start]Drop raw files here to be processed by the absorb ritual. [cite: 346]
* [cite_start]**INI File:** [cite: 347] A simple configuration file format. Sections are marked with `[names in brackets]`. [cite_start]Keys and values are separated by `=` signs. [cite: 348] Comments begin with `;` or `#`. [cite_start]`spellbook.conf` is an INI file. [cite: 349]
* [cite_start]**Non-Canon Tags:** [cite: 350] [cite_start]Tags found in notes that are not on the approved canonical list. [cite: 351] Recorded in the `non-canon-tags` file by the focus ritual. [cite_start]Reviewing this file is how you discover tags the Oracle has invented. [cite: 352]
* [cite_start]**Ollama:** [cite: 353] The local AI runtime. [cite_start]Ollama downloads and runs language models on your own machine. [cite: 354] The Spellbook uses it for zettelisation, tagging, and wiki generation. [cite_start]Ollama does not send your text to external servers. [cite: 355]
* [cite_start]**Ollama Call:** [cite: 356] The utility script `ollama_call.py`. [cite_start]Accepts a model name, a system prompt, and a user prompt, then calls Ollama and prints the response. [cite: 357] [cite_start]Used by all AI-powered scripts. [cite: 358]
* [cite_start]**Oracle:** [cite: 359] The AI model loaded in Ollama. [cite_start]Different models have different strengths — the Oracle is not a single entity but whichever model you have configured. [cite: 360]
* [cite_start]**Pipeline:** [cite: 361] [cite_start]A sequence of commands connected by pipes, where each command's output becomes the next command's input. [cite: 362] [cite_start]The absorb ritual is a four-step pipeline. [cite: 363]
* [cite_start]**Pipe:** [cite: 364] The `|` character. [cite_start]Connects two commands so that the output of the left command becomes the input of the right command. [cite: 365]
* [cite_start]**Ritual:** [cite: 366] [cite_start]A plain text file (extension `.ritual`) containing a sequence of shell commands to be run in order. [cite: 367] [cite_start]The fundamental unit of automation in the Spellbook. [cite: 368]
* [cite_start]**Script:** [cite: 369] A file containing code in any programming language. [cite_start]Scripts perform specific, reusable tasks. [cite: 370] [cite_start]They can be called from rituals, from other scripts, or directly from the terminal. [cite: 371]
* [cite_start]**Shell:** [cite: 372] The program that interprets terminal commands. [cite_start]On Mac and Linux, this is typically Bash or Zsh. [cite: 373] On Windows, it may be Command Prompt or PowerShell. [cite_start]Ritual commands are run through the shell. [cite: 374]
* [cite_start]**Sleep:** [cite: 375] The third ritual in the processing cycle. [cite_start]Uses the tag index to generate wiki pages from notes. [cite: 376] [cite_start]Corresponds to the synthesis and summarisation of accumulated knowledge. [cite: 377]
* [cite_start]**spellbook.conf:** [cite: 378] The configuration file at the root of your installation. [cite_start]Defines all paths, settings, tags, and ritual registrations. [cite: 379] [cite_start]An INI-formatted text file. [cite: 380]
* [cite_start]**Tag:** [cite: 381] [cite_start]A hashtag within a note (e.g. `#philosophy`, `#todo`) that associates it with a topic. [cite: 382] [cite_start]Tags are how the Spellbook connects notes to each other and to wiki pages. [cite: 383]
* [cite_start]**Tag Hub:** [cite: 384] A generated index file (`tag-hub-{tagname}`) listing every note associated with a given tag. [cite_start]Lives in `content/maps/tag-hub/`. [cite: 385]
* [cite_start]**Vault:** [cite: 386] [cite_start]Obsidian's term for a folder of Markdown files treated as a knowledge base. [cite: 387] [cite_start]Point Obsidian at your Spellbook installation directory to open your vault. [cite: 388]
* [cite_start]**Wiki:** [cite: 389] [cite_start]A generated summary document for a topic, written by the Oracle from all notes associated with a given tag. [cite: 390] [cite_start]Lives in `content/maps/wiki/`. [cite: 391]
* [cite_start]**Working Directory:** [cite: 392] The folder from which a command is run. [cite_start]All ritual commands execute from the directory containing `spellbook.conf`. [cite: 393]
* [cite_start]**Zettel:** [cite: 394] German for 'slip of paper.' [cite_start]An atomic note in the Zettelkasten tradition. [cite: 395] [cite_start]In the Spellbook, Zettels are identified by a 14-digit timestamp (YYYYMMDDHHMMSS) as their filename. [cite: 396]
* [cite_start]**Zettelkasten:** [cite: 397] German for 'note box.' A note-taking method based on atomic, interlinked notes. [cite_start]Developed by Niklas Luhmann. [cite: 398] [cite_start]The Spellbook's note structure is inspired by this method. [cite: 399]

[cite_start]✦ [cite: 400]
You have reached the end of the manual. [cite_start]The grimoire is yours now. [cite: 401]
[cite_start]Fill it well. [cite: 402]