# Clojure vs Python: Inter-Script Communication Conventions

> Why the Clojure and Python layers follow different rules — and why that's correct.

---

## The Two Conventions in This Codebase

**Python pipeline scripts** communicate exclusively via subprocess calls. One script
never `import`s from a sibling script. Data travels as JSON over stdin/stdout pipes.

**Clojure/Babashka scripts** call each other via `load-file` / `require`, then invoke
functions directly in-process. `spellbook_cli.clj` loads both `install_spellbook.clj`
and `create_conf.clj` this way. `install_spellbook.clj` delegates conf generation to
`create_conf/build-conf` the same way.

These look inconsistent. They aren't.

---

## Why Lisp Works Differently

Lisp (and therefore Clojure) is *homoiconic* — code and data are the same structure.
The language reader and evaluator are always present at runtime. This means:

- `load-file` is not "run another program." It is "read these forms and evaluate them
  into the current session." The loaded code becomes part of the running program,
  with full access to all namespaces, and its functions are callable directly.

- There is no meaningful distinction between "my code" and "code from another file."
  A function defined in `create_conf.clj` after a `load-file` call is exactly as
  accessible as one defined inline.

- The Clojure namespace system (`ns`, `require`) makes the source of any symbol
  explicit, so there's no ambiguity about where something came from.

Python *can* do runtime evaluation (`exec`, `importlib`, `runpy.run_path`), but:

- It's non-idiomatic for sharing module-level code between scripts.
- `import` has caching side effects (`sys.modules`) that create subtle coupling.
- The project deliberately chose subprocess to enforce a hard process boundary,
  which keeps each script independently testable and prevents import-chain failures.

---

## Why Each Convention Is Right For Its Layer

| Layer | Role | Right mechanism |
|-------|------|-----------------|
| Clojure | Orchestration — glue code that sequences and configures | In-process `load-file` / `require`. Function reuse without coupling risk. |
| Python | Pipeline workers — transform data, call LLMs, read/write files | Subprocess. Process boundary enforces clean JSON interfaces. |

The Clojure layer benefits from in-process composition: shared functions, no
serialisation overhead, full access to the same config state. The Python layer
benefits from isolation: each script is independently runnable, testable, and
replaceable without touching its neighbours.

---

## In Practice: `create_conf.clj` as Single Source of Truth

`install_spellbook.clj` and `create_conf.clj` both generate `spellbook.conf`.
Because Babashka makes in-process loading idiomatic, `install_spellbook.clj`
can simply call `create-conf/build-conf` after a `load-file` — no subprocess,
no serialisation, no duplication. `create_conf.clj` is the single source of truth
for conf structure. `install_spellbook.clj` provides the wizard UX around it.

This pattern is a direct consequence of homoiconicity: the language makes it natural
to compose programs from pieces without the coupling risks that force Python to use
process boundaries instead.

---

## Summary

The "no shared imports, use subprocess" rule applies to Python pipeline scripts.
For Babashka, in-process `load-file` is the idiomatic equivalent and carries none
of the same risks. Both conventions serve the same underlying goal: clean interfaces
and independent components. They just express it through the mechanism each language
makes natural.
