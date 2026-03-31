# Query Pipeline — Design Review & Bug Report

> Step-by-step trace of the full absorb → focus → wiki → query ritual chain,
> with identified bugs, design inconsistencies, and pre-existing issues.
> Written after implementation of the query pipeline spec (v4).

---

## Ritual Flow Summary

### absorb
```
inbox_picker.py  →  zettelkasten_llm.py  →  zettel_id_generator.py  →  tagger_llm.py
```
Picks one file from inbox, breaks it into atomic notes, assigns timestamps, tags them,
writes to `content/notes/`. Source file is left in inbox (not moved).

### focus (two separate commands, not a pipeline)
```
tag_hub_generator.py
tag_hub_populator.py
```
Step 1: Reads `[tags]` section from `spellbook.conf`, appends any extra tags file,
writes new tags to `canon-tags`, creates empty `tag-hub-{tag}` stubs for new tags.

Step 2: Walks `content/notes/`, matches `#tags` against `canon-tags`, overwrites
each `tag-hub-{tag}` file with a sorted list of matching filenames.

### wiki
```
wiki_generator_llm.py
```
Reads `canon-tags`, iterates each tag, reads its `tag-hub-{tag}` file, opens
each listed zettel's `Source: [[...]]` file from disk, calls LLM, writes wiki to
`content/maps/wiki/{tag}.md`.

### query (new pipeline)
```
query_args_handler.py  →  query_tagger.py  →  wiki_retriever.py
  →  zettel_aggregator.py  →  query_ranker.py  →  context_assembler.py  →  query_llm.py
```

---

## Bugs in New Code

### B01 — `context_assembler.py`: archive_dir read inside source-extraction loop

**File:** `infrastructure/scripts/context_assembler.py`

**What happens:** When `include_sources=True`, the script extracts `Source: [[...]]`
links from each ranked zettel and tries to open those files. The current code calls
`get_config("spellbook", "archive")` inside the loop — once per zettel that has a
Source field. Each call spawns a `python3 config_reader.py` subprocess.

**Impact:** Performance. With 10 ranked zettels, that's up to 10 subprocess spawns
for a value that doesn't change. Not a crash, but noticeable on slower hardware.
`include_sources` is off by default, so this only triggers explicitly.

**Fix:** Move the `archive_dir` read to before the loop.

```python
# Before the loop:
try:
    archive_dir = get_config("spellbook", "archive")
except subprocess.CalledProcessError:
    archive_dir = ""

for zettel in ranked_zettels:
    match = SOURCE_PATTERN.search(zettel["content"])
    ...
```

---

### B02 — `context_assembler.py`: source path resolution doesn't match `wiki_generator_llm.py`

**File:** `infrastructure/scripts/context_assembler.py`

**What happens:** `context_assembler.py` resolves relative Source paths by joining
with `archive_dir`:
```python
source_path = source_ref if os.path.isabs(source_ref) else os.path.join(archive_dir, source_ref)
```

`wiki_generator_llm.py` does this instead:
```python
if os.path.exists(source_path):   # source_path = raw match, CWD-relative
```

The spellbook runner sets CWD to the spellbook root (where `spellbook.conf` lives).
So `wiki_generator_llm.py` resolves relative paths from the spellbook root. Source
links in zettels are likely absolute paths to inbox files, or paths relative to root.
Prepending `archive_dir` is the wrong base.

**Impact:** `include_sources=True` will likely warn "source file not found on disk"
for every zettel, even when the files exist, unless source paths happen to be absolute.
Off by default, so not critical — but the feature won't work correctly when enabled.

**Fix:** Mirror `wiki_generator_llm.py`'s approach — check the raw path first, then
fall back to prefixing with root or archive:

```python
try:
    root_dir = get_config("spellbook", "root")
    archive_dir = get_config("spellbook", "archive")
except subprocess.CalledProcessError:
    root_dir = ""
    archive_dir = ""

for zettel in ranked_zettels:
    match = SOURCE_PATTERN.search(zettel["content"])
    if not match:
        continue
    source_ref = match.group(1).strip()
    # Try: absolute, then CWD-relative (spellbook root), then archive-relative
    candidates = [source_ref,
                  os.path.join(root_dir, source_ref),
                  os.path.join(archive_dir, source_ref)]
    source_path = next((p for p in candidates if os.path.exists(p)), None)
    if source_path is None:
        sys.stderr.write(f"Warning: source file not found on disk: {source_ref}\n")
        continue
    with open(source_path, ...) as f:
        source_texts.append(f.read())
```

---

## Pre-existing Bugs / Design Inconsistencies

These were not introduced by the query implementation but are relevant to the full
chain. Flagged for awareness. The spec says not to modify these files.

### P01 — `tag_hub_generator.py` and `tag_hub_populator.py` violate "no shared imports"

Both scripts do:
```python
from config_reader import find_config, load_config
```

This directly contradicts the design philosophy:
> No shared imports between scripts. Each script must be independently executable.
> Inter-script communication happens via subprocess calls only.

If `config_reader.py` is ever moved, renamed, or its internal API changed, both
scripts silently break. Every other script uses the subprocess pattern.

Also noteworthy: both scripts have their own path-resolution logic inside `__main__`
rather than calling `get_config("spellbook", "taghub")`. This is inconsistent with
every other script in the codebase.

---

### P02 — `tag_hub_generator.py` derives taghub path from `maps`, not `taghub` key

```python
taghub = os.path.join(_resolve(_config.get('spellbook', 'maps')), 'tag-hub')
```

All new query scripts use:
```python
taghub_dir = get_config("spellbook", "taghub")
```

In the standard layout these resolve to the same directory, so this isn't currently
broken. But if a user ever sets a non-standard `taghub` path in `spellbook.conf`
(e.g. pointing to a shared location), `focus` writes to `maps/tag-hub` while `query`
reads from whatever `taghub` points to. They would diverge silently.

---

### P03 — `tagger_llm.py` uses `parse_args()` not `parse_known_args()`

```python
return parser.parse_args()   # line 48 of tagger_llm.py
```

The spec requires all pipeline scripts to use `parse_known_args()`. With the
`insert-args-first-stage` fix now routing trailing CLI args to the FIRST pipeline
stage, `tagger_llm.py` no longer receives unexpected args in normal usage. So this
won't crash under normal operation.

However, if the absorb ritual were ever extended to have extra pipeline stages that
pass unknown flags through, `tagger_llm.py` would crash. Low risk now, but the
inconsistency is there.

---

### P04 — `wiki_generator_llm.py` only generates wikis for tags that have Source links in their zettels

When a zettel has no `Source: [[...]]` match, `wiki_generator_llm.py` appends
`#error` to that zettel and skips it. A tag whose zettels all lack Source links gets
no wiki page. This means `wiki_retriever.py` finds no wiki for that tag even though
the tag has notes in the knowledge base. Downstream, context_assembler.py would have
no wiki content for that tag — a silent degradation.

Not a bug introduced here, but relevant to understanding why query results might be
sparse even after a full absorb → focus → wiki run.

---

## Design Gaps

### D01 — query pipeline requires wiki ritual; prerequisite is implicit

`wiki_retriever.py` exits 1 with an error if the wiki directory doesn't exist:
```python
if not os.path.isdir(wiki_dir):
    sys.stderr.write(f"Error: wiki directory not found at {wiki_dir}.\n")
    sys.exit(1)
```

This is correct per spec. But it means `spellbook query` will fail at stage 3
with a confusing error if the user has never run `spellbook wiki`. The required
ritual order (absorb → focus → wiki → query) is not communicated anywhere to users.

**Suggestion:** The error message could be made more explicit:
```
Error: wiki directory not found at {wiki_dir}.
Run 'spellbook wiki' first to generate wiki pages.
```

Alternatively, the spec could be revisited to allow `wiki_retriever.py` to warn
and continue with `wikis = []` if the directory is missing. Either is valid;
just needs a deliberate choice.

---

### D02 — `run-ritual!` applies `insert-args-first-stage` to every command in a multi-line ritual

The modified `run-ritual!` loop applies the fix to each command it encounters:

```clojure
(loop [[cmd & rest-cmds] commands step 0]
  ...
  (let [full-cmd (if args-str
                   (insert-args-first-stage expanded args-str)
                   expanded)]
```

For a multi-command ritual like `focus` (two non-pipeline lines), if extra-args
were ever passed, BOTH commands would receive them. This matches the old behaviour
(`str cmd args-str` on every command) so there's no regression.

But the semantic contract is: "trailing CLI args are input data for the pipeline."
In a multi-command ritual the "first pipeline stage" concept doesn't map cleanly.
The current implementation is safe for all existing rituals (none take extra-args
except `query`, which is a single-line pipeline). Worth documenting as a known
edge case if multi-line rituals with user input are ever added.

---

### D03 — Single `query_model` key used for both tagging (light) and synthesis (heavy)

The design philosophy distinguishes light vs heavy models:
- Tagging: `granite4:3b` (fast, light)
- Synthesis: `cogito:8b` (slow, more capable)

Both `query_tagger.py` and `query_llm.py` use the same three-step resolution:
`query_model` → `ollama_model` → script default

With `query_model = cogito:8b` in `spellbook.conf`, both scripts use `cogito:8b`.
The script-level defaults (`granite4:3b` for tagger, `cogito:8b` for LLM) only
activate when BOTH `query_model` and `ollama_model` are absent.

In practice this is fine — `cogito:8b` will handle tagging correctly, just more
slowly than necessary. But there's no conf-level way to use different models for
the two tasks without editing the scripts. The existing pattern has separate keys
(`tagger_model`, `wiki_model`, `zettel_model`) which avoids this problem.

**Suggestion:** Add `query_tagger_model` to `spellbook.conf` and use it as the
first fallback in `query_tagger.py` before `query_model`. Follows the established
pattern.

---

## Minor Spec Deviation (Harmless)

### S01 — `query_args_handler.py` uses `if remaining:` not `if sys.argv[1:]:`

The spec's priority order says: "if `sys.argv[1:]` is non-empty, use argparse."
The implementation instead checks `if remaining:` (the non-flag positional words).

**Why this diverges:** Consider `echo "stoicism" | spellbook query --no-wikis`.
- `sys.argv[1:]` = `["--no-wikis"]` (non-empty per spec)
- `remaining` = `[]` (no positional words)
- Spec says: trailing args mode → query = "" → exit 2
- Implementation says: remaining empty → falls through to stdin mode → query = "stoicism" ✓

The implementation handles this case correctly and more usefully. The strict spec
reading would make the piped-with-flags pattern impossible to use.

No fix needed — this is an improvement over the spec.

---

## Full Trace: `spellbook query what is logic`

```
1. spellbook_cli.clj
   extra-args = ["what", "is", "logic"]
   args-str   = " what is logic"
   ritual cmd = "python3 .../query_args_handler.py | python3 .../query_tagger.py | ..."

   insert-args-first-stage finds first "|":
   before = "python3 .../query_args_handler.py"        (str/trimr applied)
   after  = "| python3 .../query_tagger.py | ..."
   result = "python3 .../query_args_handler.py what is logic| python3 ..."
   (shell accepts | without leading space — valid bash)

2. query_args_handler.py
   sys.argv[1:] = ["what", "is", "logic"]
   remaining    = ["what", "is", "logic"]
   query        = "what is logic"
   flags read from [query-args-handler] conf section (all defaults)
   → stdout: {"query":"what is logic","flags":{"no_wikis":false,...}}

3. query_tagger.py
   reads canon-tags, calls LLM with query + tag list
   → stdout: {..., "tags":["logic","philosophy"]}   (example)

4. wiki_retriever.py
   checks wiki_dir/logic.md, wiki_dir/philosophy.md
   reads any that exist
   → stdout: {..., "wikis":[{"tag":"logic","path":"...","content":"..."}]}

5. zettel_aggregator.py
   reads tag-hub-logic, tag-hub-philosophy
   union of filenames, deduped
   reads each zettel file, extracts #tags via regex
   → stdout: {..., "zettels":[{id, path, content, tags, score:0}, ...]}

6. query_ranker.py
   scores by tag overlap: score = len({"logic","philosophy"} & zettel["tags"])
   sorts desc by score, then id (tie-break: newer first)
   takes top 10
   → stdout: {..., "ranked_zettels":[...]}

7. context_assembler.py
   envelope flags take precedence over argparse (no_wikis=false → include wikis)
   assembles:
     ## Query
     what is logic

     ## Relevant Wiki Pages
     {wiki content}

     ## Relevant Notes
     {zettel content}
   → stdout: {..., "context":"## Query\n..."}

8. query_llm.py --mode prose
   context >= 100 chars → no empty-context prefix
   calls LLM with system prompt + context + question
   prints response as plain text to stdout (terminal)
   → terminal: "Logic is the study of valid reasoning..."
```

---

## Required Fixes (Priority Order)

| # | File | Issue | Severity |
|---|------|-------|----------|
| B02 | `context_assembler.py` | Source path resolution wrong base | Medium (feature broken when enabled) |
| B01 | `context_assembler.py` | archive_dir read inside loop | Low (performance only) |
| D01 | `wiki_retriever.py` error msg | Prerequisite not communicated | Low (UX) |
| D03 | `spellbook.conf` | No separate tagger/LLM model keys | Low (design debt) |
