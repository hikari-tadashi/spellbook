#!/usr/bin/env bb

;; =============================================================================
;;  create_conf.clj — Single source of truth for spellbook.conf structure.
;;
;;  Used directly as a minimal setup tool (prompts for root dir, writes conf
;;  with sensible defaults), and loaded by install_spellbook.clj to generate
;;  the conf with user-supplied Ollama host and model values.
;;
;;  Usage (standalone):
;;    bb create_conf.clj
;; =============================================================================

(ns create-conf
  (:require [babashka.fs :as fs]
            [clojure.string :as str]))

;; ---------------------------------------------------------------------------
;; Helpers
;; ---------------------------------------------------------------------------

(def windows?
  (str/starts-with? (str/lower-case (System/getProperty "os.name")) "windows"))

(def sep (if windows? "\\" "/"))

(defn home []
  (if windows?
    (or (System/getenv "USERPROFILE") (System/getProperty "user.home"))
    (System/getProperty "user.home")))

(defn p [& parts]
  (str (apply fs/path (map str parts))))

;; ---------------------------------------------------------------------------
;; Conf generation — single source of truth for spellbook.conf structure.
;;
;; Called by this script's own -main (with hardcoded defaults) and by
;; install_spellbook.clj (with user-supplied values from the install wizard).
;; ---------------------------------------------------------------------------

(defn build-conf [root ollama-host ollama-model]
  (str/join "\n"
    ["; +============================================================+"
     "; |             * S P E L L B O O K . C O N F *              |"
     "; +============================================================+"
     ""
     "[alias]"
     "; ── Personal Life ───────────────────────────────────────────────"
     "contacts     = people"
     "person       = people"
     "friend       = people"
     "family       = people"
     "colleague    = people"
     ""
     "diary        = journal"
     "log          = journal"
     "reflection   = journal"
     ""
     "appointment  = events"
     "event        = events"
     "birthday     = events"
     "meeting      = meetings"
     ""
     "; ── Work & Projects ─────────────────────────────────────────────"
     "tasks        = todo"
     "task         = todo"
     "action       = todo"
     ""
     "project      = projects"
     "initiative   = projects"
     ""
     "decision     = decisions"
     "choice       = decisions"
     ""
     "goal         = goals"
     "objective    = goals"
     "okr          = goals"
     ""
     "; ── Learning & Knowledge ────────────────────────────────────────"
     "book-notes   = book"
     "read         = book"
     "reading      = book"
     ""
     "note         = reference"
     "notes        = reference"
     "resource     = reference"
     ""
     "concept      = idea"
     "insight      = idea"
     "thought      = idea"
     ""
     "; ── Domains ─────────────────────────────────────────────────────"
     "tech         = technology"
     "code         = technology"
     "software     = technology"
     ""
     "money        = finances"
     "budget       = finances"
     "spending     = finances"
     ""
     "politics     = politics"
     "news         = culture"
     ""
     "; ── Creative ────────────────────────────────────────────────────"
     "fiction      = writing"
     "essay        = writing"
     "blog         = writing"
     ""
     "drawing      = art"
     "painting     = art"
     "photography  = art"
     ""
     "[commands]"
     "; Move a file to the journal directory"
     (str "journal = mv $filename content" sep "journal")
     ""
     "[tags]"
     "; ── System ─────────────────────────────────────────────────────"
     "; Tags the Spellbook itself uses for routing and housekeeping"
     "todo" "inbox" "reference" "archive"
     ""
     "; ── Personal Life ───────────────────────────────────────────────"
     "journal" "people" "events" "health" "finances" "home" "travel"
     ""
     "; ── Work & Projects ─────────────────────────────────────────────"
     "work" "projects" "meetings" "decisions" "goals"
     ""
     "; ── Learning & Knowledge ────────────────────────────────────────"
     "learning" "book" "article" "course" "idea" "question"
     ""
     "; ── Domains ─────────────────────────────────────────────────────"
     "; Broad enough to be universally useful; users add their own"
     "science" "technology" "history" "philosophy" "economics"
     "politics" "culture" "art" "language"
     ""
     "; ── Creative ────────────────────────────────────────────────────"
     "writing" "music" "design"
     ""
     "[spellbook]"
     (str "root          = " root)
     (str "inbox         = " (p root "inbox"))
     (str "archive       = " (p root "content" "archive"))
     (str "notes         = " (p root "content" "notes"))
     (str "journal       = " (p root "content" "journal"))
     (str "maps          = " (p root "content" "maps"))
     (str "taghub        = " (p root "content" "maps" "tag-hub"))
     (str "wiki          = " (p root "content" "maps" "wiki"))
     (str "hubs          = " (p root "content" "maps" "hubs"))
     (str "backlinks     = " (p root "content" "maps" "backlinks"))
     (str "scripts       = " (p root "infrastructure" "scripts"))
     (str "documentation = " (p root "infrastructure" "documentation"))
     (str "rituals       = " (p root "infrastructure" "rituals"))
     (str "oracle_host   = " ollama-host)
     (str "oracle_model  = " ollama-model)
     "query_max_results  = 10"
     "plugin_sigil  ="
     ""
     "; Query args defaults — these can be overridden at invocation time."
     "; See: spellbook query --help"
     "[query-args-handler]"
     "no-wikis        = false"
     "no-zettels      = false"
     "include-sources = false"
     "mode            = prose"
     ""
     "; Rituals registered explicitly by name=path."
     "; These override any same-named .ritual file in the rituals/ directory."
     "[rituals]"
     (str "sleep         = " (p root "infrastructure" "rituals" "sleep.ritual"))
     (str "reset         = " (p root "infrastructure" "rituals" "reset.ritual"))
     (str "query         = " (p root "infrastructure" "rituals" "query.ritual"))
     (str "wiki          = " (p root "infrastructure" "rituals" "wiki.ritual"))
     ""
     "[spellbook-ignored]"
     "\"infrastructure\"" "\"projects\""
     "\"archive\"" "\"assets\"" "\"maps\""]))

;; ---------------------------------------------------------------------------
;; Entry point
;; ---------------------------------------------------------------------------

(defn -main [& _args]
  (let [default-dir (p (home) "Documents" "spellbook")
        _           (print (str "[?] Root directory [" default-dir "]: "))
        _           (flush)
        input       (str/trim (or (read-line) ""))
        install-dir (str (fs/expand-home (if (str/blank? input) default-dir input)))
        out-path    (p install-dir "spellbook.conf")]

    (println (str "[*] Writing : " out-path))

    (when (fs/exists? out-path)
      (println (str "[!] spellbook.conf already exists at: " out-path))
      (print    "    Overwrite? (y/N): ")
      (flush)
      (when (not= "y" (str/lower-case (str/trim (or (read-line) ""))))
        (println "[X] Aborted.")
        (System/exit 0)))

    (spit out-path (build-conf install-dir "127.0.0.1:11434" "llama3.1:8b"))
    (println (str "[OK] spellbook.conf written to: " out-path))))

(when (= *file* (System/getProperty "babashka.file"))
  (apply -main *command-line-args*))
