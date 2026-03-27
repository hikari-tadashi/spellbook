# ✦  P L U G I N S  ✦

*A Supplement to the Field Manual for the Apprentice Archivist*

*Narrated by the Install Wizard*

*who has, in the years since you last met, developed strong opinions*
*about the value of interchangeable parts.*

---

## A Word Before We Begin

*You have mastered the Spellbook's core cycle. You know how to drop a note into the inbox, run the absorb ritual, watch the Oracle atomise your thoughts and file them. You know how focus builds the index, how sleep synthesises the wiki. The system works. You use it.*

*And then one day you think: I wish it could also handle PDFs. Or: I have a folder of audio transcripts I'd like to ingest. Or: I want to write a ritual that calls a custom script I wrote, and I'd like to be able to reference it cleanly, without typing its full path every time.*

*That is what plugins are for.*

This document teaches you how the Spellbook's plugin system works, how to build your own plugins, and — for those who want to understand the full picture — how the system is designed to be replaced, extended, or reimagined entirely. It is written for practitioners at every level of comfort. If you have never written a Python script, the first few sections will serve you. If you have written a language runtime from scratch, the later sections will hold your interest.

You do not need to read this linearly. Start where your curiosity lands.

---

## Part I — What a Plugin Is

*There is a long tradition, in software as in craft, of building things that can be extended by the people who use them. A loom that accepts interchangeable reeds. A workbench with a standard mounting rail. A text editor whose every behaviour can be rewritten by the person sitting at the keyboard. The Spellbook follows this tradition.*

The Spellbook's core scripts — `inbox_picker.py`, `zettelkasten_llm.py`, `tagger_llm.py` and the rest — are each responsible for exactly one thing. They communicate by passing data through pipes. A ritual is nothing more than a description of how to connect them.

A plugin is an extension to this system. It lives in its own folder inside `infrastructure/plugins/`. It can contribute two things:

**Rituals** — new named commands that become available to the Spellbook CLI, just as if you had placed a `.ritual` file in `infrastructure/rituals/` yourself.

**Components** — named shortcuts for pipeline steps, so that instead of writing the full path to a script every time you want to use it in a ritual, you can write a short, readable name like `pdf-reader.to_text`.

That is the whole model. A plugin is a folder with a small configuration file and whatever scripts and ritual files it needs to do its job.

---

## Part II — How the System Works

*Before you build something, it helps to understand how the machinery that will run it actually operates. This section is that machinery, described plainly.*

### Discovery

When you invoke any Spellbook ritual, the CLI runs through a three-stage discovery process to find all available rituals. The stages are listed here from lowest to highest priority — meaning that later stages can override earlier ones.

**Stage 1 — Plugins.** The CLI scans `infrastructure/plugins/` for subdirectories that contain a `plugin.conf` file. For each one it finds, it reads the conf and registers any rituals and components the plugin declares.

**Stage 2 — The rituals directory.** The CLI scans `infrastructure/rituals/` for `.ritual` files, as it always has.

**Stage 3 — Your spellbook.conf.** Explicit entries in the `[rituals]` section of your `spellbook.conf` are registered last, and take precedence over everything else.

This means you can always override a plugin's ritual by placing a same-named `.ritual` file in `infrastructure/rituals/`, and you can always override that by registering the name explicitly in your conf. Your own configuration is always the final word.

### The Component Registry

When the CLI discovers a plugin's components, it builds an internal registry — a lookup table that maps short names to full shell invocations. When you write `pdf-reader.to_text` inside a ritual file, the CLI looks up that token in the registry before passing the line to the shell, and replaces it with the full invocation. The shell never sees the short name. It only sees a valid command.

This expansion happens transparently. From the shell's perspective, every ritual line is a normal sequence of programs and pipes. The short names are a convenience for the human writing the ritual, not a new syntax the shell has to understand.

### The Path Guard

The CLI is careful not to expand tokens that refer to real files. Before expanding a component reference, it checks whether a file with that name exists at the spellbook root. If it does, the token is left alone — it is a real path, not a component reference. This prevents the system from accidentally expanding something it should not.

---

## Part III — Your First Plugin

*The best way to understand a thing is to build one. We are going to build a simple plugin together — a PDF reader that extracts text from PDF files and feeds them into the standard absorb pipeline. It is practical, it is a common need, and it touches every part of the plugin system.*

### Step 1 — Create the Plugin Directory

Inside `infrastructure/plugins/`, create a new folder. Name it `pdf-reader`.

```
infrastructure/plugins/
  pdf-reader/
```

Nothing else is required yet. The folder exists.

### Step 2 — Write the plugin.conf

Create a file named `plugin.conf` inside `pdf-reader/`. This is the file that tells the Spellbook that this directory is a plugin. Without it, the directory is invisible to the system.

```ini
[plugin]
name    = pdf-reader
version = 1.0
rituals = rituals/

[components]
to_text = python3 scripts/pdf_to_text.py
```

The `[plugin]` section declares the plugin's identity. The `name` is used as the prefix for all component references from this plugin — so `to_text` becomes `pdf-reader.to_text`. The `rituals` key tells the CLI where to find this plugin's ritual files; if you leave it out, the CLI will look for `.ritual` files directly in the plugin's root directory.

The `[components]` section maps short names to shell invocations. The path on the right (`scripts/pdf_to_text.py`) is relative to the plugin directory. The CLI resolves it to a full path relative to the spellbook root before passing it to the shell.

### Step 3 — Write the Script

Create `infrastructure/plugins/pdf-reader/scripts/pdf_to_text.py`. This script receives a file path (from stdin, matching the conventions of the rest of the pipeline) and prints the extracted text to stdout.

A minimal version using the `pdfminer.six` library:

```python
#!/usr/bin/env python3
"""
pdf_to_text.py — Extracts plain text from a PDF file.
Reads a file path from stdin. Prints extracted text to stdout.
"""
import sys
from pdfminer.high_level import extract_text

filepath = sys.stdin.read().strip()
if not filepath:
    sys.stderr.write("Error: No file path provided.\n")
    sys.exit(1)

try:
    text = extract_text(filepath)
    print(text)
except Exception as e:
    sys.stderr.write(f"Error: {e}\n")
    sys.exit(1)
```

The script follows the Spellbook's standard conventions: reads from stdin, writes to stdout, exits with a non-zero code on failure. This is what makes it composable with the rest of the pipeline.

### Step 4 — Write the Ritual

Create `infrastructure/plugins/pdf-reader/rituals/pdf-ingest.ritual`.

```
# pdf-ingest.ritual
# Picks a PDF from the inbox, extracts its text, and absorbs it.
python3 infrastructure/scripts/inbox_picker.py | pdf-reader.to_text | python3 infrastructure/scripts/zettelkasten_llm.py | python3 infrastructure/scripts/zettel_id_generator.py | python3 infrastructure/scripts/tagger_llm.py
```

Notice how `pdf-reader.to_text` sits naturally in the pipeline alongside the standard scripts. It reads like a description of the process, not like a configuration file. The CLI replaces it with the full invocation before anything runs.

### Step 5 — Verify

From your spellbook directory, run:

```
bb infrastructure/scripts/spellbook_cli.clj list
```

You should see `pdf-ingest` in the list of available rituals. Drop a PDF into your inbox and run:

```
bb infrastructure/scripts/spellbook_cli.clj pdf-ingest
```

That is a complete plugin.

---

## Part IV — The plugin.conf in Full

*The configuration file is small by design. It carries only what the system needs to know, and nothing more. Here is every key it understands.*

### The `[plugin]` Section

This section is required. Without it, the directory is not treated as a plugin.

| Key | Required | Description |
|-----|----------|-------------|
| `name` | Yes | The plugin's name. Used as the prefix for all component references: `name.component`. By convention, matches the directory name, but does not have to. |
| `version` | No | A version string. Not used by the system; provided for your own reference. |
| `rituals` | No | Path to the directory containing this plugin's `.ritual` files, relative to the plugin directory. If omitted, the plugin directory itself is scanned for `.ritual` files. |

### The `[components]` Section

This section is optional. Omit it entirely if your plugin ships only rituals.

Each entry maps a component name to a shell invocation:

```ini
[components]
name = interpreter path/to/script [optional fixed args]
```

The interpreter is declared explicitly — `python3`, `node`, `ruby`, whatever is appropriate. Do not rely on the file's extension or shebang line. This is the same convention the Spellbook's own ritual files use, and it ensures the plugin works identically on every platform.

The path is relative to the plugin directory. The CLI resolves it to a path relative to the spellbook root when expanding the token.

You can include fixed arguments after the path. These are appended to every invocation of the component, before any arguments the ritual supplies:

```ini
[components]
to_text      = python3 scripts/pdf_to_text.py
chunk_text   = python3 scripts/pdf_to_text.py --chunk-size 500
```

Here `to_text` and `chunk_text` point to the same script but with different behaviour. Both are valid component references.

---

## Part V — Using Components in Ritual Files

*A component reference looks like a name. Two names, joined by a dot — the plugin's name on the left, the component's name on the right. This is the only syntax the plugin system adds to ritual files. Everything else is ordinary shell.*

### The Basic Form

```
plugin-name.component-name
```

In the context of a full ritual line:

```
python3 infrastructure/scripts/inbox_picker.py | pdf-reader.to_text | python3 infrastructure/scripts/zettelkasten_llm.py
```

The dot is the separator. Hyphens are allowed in both parts. No spaces around the dot.

### The Sigil

Some practitioners prefer their component references to be visually distinct from regular commands — especially as rituals grow longer and more complex. The Spellbook supports an optional sigil character, configured in `spellbook.conf`:

```ini
[spellbook]
plugin_sigil = @
```

With a sigil configured, the CLI only expands tokens that begin with that character:

```
python3 infrastructure/scripts/inbox_picker.py | @pdf-reader.to_text | python3 infrastructure/scripts/zettelkasten_llm.py
```

The sigil is stripped before the registry lookup. The registry always stores bare `plugin.component` keys, so the plugin itself never needs to know whether its user has configured a sigil.

The default is no sigil. Most practitioners will not need one. If you find yourself writing rituals with many component references and want the references to stand out at a glance, the sigil is there for you.

| Setting | Ritual syntax | Notes |
|---------|---------------|-------|
| `plugin_sigil =` (empty) | `pdf-reader.to_text` | Default. Any `word.word` token matching a registered component is expanded. |
| `plugin_sigil = @` | `@pdf-reader.to_text` | Only `@`-prefixed tokens are candidates for expansion. |

---

## Part VI — Flexibility and Reach

*Here the manual addresses a different kind of reader — one who is not looking to add a PDF reader, but to understand how far this system can be taken. How much of the Spellbook can be replaced? How much can be extended? What are the actual limits?*

### What Plugins Can Do

Plugins are not limited to adding new file-format handlers. They are not limited to adding new rituals. A plugin can do anything a ritual or a script can do, which means it can do essentially anything.

Some examples of what plugins have been or could be used for:

**Alternative oracles.** A plugin can ship its own `oracle_call.py` that speaks to a different AI backend — the Anthropic API, a remote Ollama instance, a locally running GPT4All. Register it as a component and reference it in place of `ollama_call.py` in any ritual.

**Pre-processing pipelines.** A plugin can insert steps before the zettelkasten script — cleaning HTML from web clips, stripping email headers, normalising encoding. These steps are invisible to the rest of the system; they just emit clean text.

**Post-processing and export.** A plugin can add rituals that read from `content/notes/` or `content/maps/wiki/` and export to other formats — EPUB, Anki flashcard decks, HTML sites, daily digest emails to yourself.

**Entirely parallel pipelines.** A plugin can ship rituals that have nothing to do with the absorb/focus/sleep cycle. A `journal` ritual. A `review` ritual that surfaces notes you haven't read in thirty days. A `backup` ritual. The plugin system does not prescribe the purpose of the rituals it discovers — it only makes them available.

**Custom dispatchers.** If you want to replace the CLI itself — perhaps with one that runs rituals asynchronously, or compiles them to a lock file before execution, or adds a web interface — the plugin discovery system is designed to be callable independently. Feed it a conf path, receive a JSON registry of rituals and components. Pipe that into your own dispatcher. The Spellbook's internal machinery is available to anyone who wants to build on top of it or around it.

### What Plugins Cannot Override

The only thing a plugin cannot do through the plugin system alone is override an explicit `[rituals]` entry in `spellbook.conf`. Those entries are the user's final word. If you want your plugin's ritual to be available under a different name for a specific user, the user adds that name to their conf. The plugin does not reach into the conf itself.

This is a feature, not a limitation. It means a user who installs a plugin they only partially trust cannot have that plugin hijack a ritual they've already named.

### A Note on Structure

The plugin system enforces exactly one structural requirement: the presence of `plugin.conf` at the plugin directory's root. Everything else — where scripts live, what language they're written in, whether they have subdirectories, whether they ship a `README` — is entirely up to the plugin author.

This is deliberate. A plugin for extracting text from PDFs and a plugin for syncing notes to a remote server have almost nothing in common. Imposing a shared directory layout would serve neither well. The `plugin.conf` is the handshake; the rest of the plugin is the plugin's own business.

---

## Part VII — Collisions, Priority, and When Things Go Wrong

*Two wizards occasionally reach for the same name. The system handles this gracefully, but it is worth understanding what "gracefully" means in practice.*

### Two Plugins with the Same Ritual Name

If two plugins register a ritual with the same name, the CLI warns you at discovery time — printing a message to stderr that names the collision — and the plugin discovered first alphabetically wins. The ritual still runs; nothing breaks. You are simply informed that two plugins wanted the same name and that one of them lost.

To resolve this permanently, add an explicit entry to `spellbook.conf`:

```ini
[rituals]
pdf-ingest = infrastructure/plugins/my-preferred-plugin/rituals/pdf-ingest.ritual
```

Explicit entries in `[rituals]` always win. The collision disappears.

### Two Plugins with the Same Component Key

The same rule applies. `plugin-name.component-name` is the full key, so a collision requires two plugins with the same `name` value in their `[plugin]` sections registering a component with the same name. This is unlikely in practice but handled the same way: warn, first alphabetically wins, user conf resolves it if needed.

### A Component Reference That Doesn't Expand

If you write a component reference in a ritual and the CLI does not find it in the registry, the token passes through to the shell unchanged. The shell will then fail to execute it and return a non-zero exit code, which stops the ritual. This is the intended behaviour — the failure is visible and immediate, and the ritual file itself tells you exactly which token caused the problem.

If you find a component reference unexpectedly not expanding, check:

1. The plugin directory contains `plugin.conf`.
2. The `name` in `[plugin]` matches the prefix you used in the ritual.
3. The component name in `[components]` matches the suffix you used.
4. If a sigil is configured, the token in the ritual begins with the sigil character.
5. A file with that name does not exist at the spellbook root (which would trigger the path guard and suppress expansion).

### A Plugin That Fails Silently

A plugin directory without a `plugin.conf` is ignored completely — no warning, no error. This is intentional: `infrastructure/plugins/` may contain work-in-progress directories, disabled plugins renamed to `pdf-reader.disabled`, or documentation folders. Only directories with a valid `plugin.conf` are treated as plugins.

If your plugin is not appearing in `spellbook list`, the most likely cause is a missing or malformed `plugin.conf` — specifically, one that does not contain a `[plugin]` section.

---

## Reference

### Plugin Directory Layout (Recommended)

```
infrastructure/plugins/
  your-plugin/
    plugin.conf          ← required
    rituals/
      your-ritual.ritual ← becomes the "your-ritual" command
    scripts/
      your_script.py     ← referenced in plugin.conf [components]
    README.md            ← optional; ignored by the system
```

### plugin.conf Quick Reference

```ini
[plugin]
name    = your-plugin   ; required
version = 1.0           ; optional

; Where .ritual files live, relative to this file.
; Defaults to scanning the plugin root if omitted.
rituals = rituals/

[components]
; name = interpreter path/to/script [optional fixed args]
; Path is relative to the plugin directory.
do_thing   = python3 scripts/your_script.py
do_other   = node scripts/other.js --flag value
```

### spellbook.conf Plugin Settings

```ini
[spellbook]
; The sigil character that prefixes component references in ritual files.
; Leave empty (default) for no sigil: pdf-reader.to_text
; Set to a character for sigil mode: @pdf-reader.to_text
plugin_sigil =
```

### Priority Order (Rituals)

From lowest to highest priority. Higher entries override lower ones.

| Priority | Source |
|----------|--------|
| 1 (lowest) | Plugin rituals discovered from `infrastructure/plugins/` |
| 2 | Rituals discovered from `infrastructure/rituals/` |
| 3 (highest) | Explicit `[rituals]` entries in `spellbook.conf` |

### Glossary Additions

**Plugin** — A self-contained extension to the Spellbook, living in `infrastructure/plugins/`, identified by the presence of a `plugin.conf` file. A plugin may contribute rituals, pipeline components, or both.

**Component** — A named pipeline step registered by a plugin. Referenced in ritual files as `plugin-name.component-name`. Expanded to a full shell invocation by the CLI before the line is passed to the shell.

**Component Registry** — The internal lookup table the CLI builds at startup from all discovered plugin components. Maps short component keys to full invocation strings.

**Sigil** — An optional prefix character (configured via `plugin_sigil` in `spellbook.conf`) that marks component references in ritual files. With no sigil configured, all `word.word` tokens matching a registry key are expanded.

**plugin.conf** — The INI-format configuration file that identifies a directory as a Spellbook plugin and declares its rituals directory and component invocations.

---

*The grimoire grows in the direction of its keeper's needs.*

*Add what you need. Leave what you don't.*

*The plugins directory is patient.*
