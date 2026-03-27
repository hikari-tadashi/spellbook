#!/usr/bin/env bb

;; =============================================================================
;;  * THE SPELLBOOK INSTALL WIZARD * (Cross-Platform Edition)
;;
;;  The secrets are closely guarded, so another wizard has to install it
;;  for you... but fear not -- this wizard is quite friendly.
;;
;;  Usage:  bb install_spellbook.clj [optional_config.conf]
;; =============================================================================

(ns install-spellbook
  (:require [babashka.fs      :as fs]
            [babashka.process :as proc]
            [clojure.java.io  :as io]
            [clojure.string   :as str]))

;; ── ANSI Colors ───────────────────────────────────────────────────────────────

(def ESC     "\u001B")
(def CYAN    (str ESC "[36m"))
(def GREEN   (str ESC "[32m"))
(def YELLOW  (str ESC "[33m"))
(def RED     (str ESC "[31m"))
(def MAGENTA (str ESC "[35m"))
(def DIM     (str ESC "[2m"))
(def BOLD    (str ESC "[1m"))
(def RESET   (str ESC "[0m"))

;; ── OS Detection ──────────────────────────────────────────────────────────────

(def os-name  (str/lower-case (System/getProperty "os.name")))
(def windows? (str/starts-with? os-name "windows"))
(def mac?     (str/starts-with? os-name "mac"))

(defn home-dir
  "Returns the user's home directory as a string, platform-aware."
  []
  (if windows?
    (or (System/getenv "USERPROFILE")
        (System/getProperty "user.home"))
    (System/getProperty "user.home")))

;; ── Path Helper ───────────────────────────────────────────────────────────────

(defn p
  "Build a native OS path string from parts using babashka.fs/path."
  [& parts]
  (str (apply fs/path (map str parts))))

(defn expand-path
  "Expand a leading ~ to the user's home directory, using the correct
  path separator for the current platform."
  [path]
  (when path
    (if (str/starts-with? path "~")
      (let [after-tilde (str/replace-first path #"^~[/\\]?" "")]
        (if (str/blank? after-tilde)
          (home-dir)
          (str (fs/path (home-dir) after-tilde))))
      path)))

;; ── Print Helpers ─────────────────────────────────────────────────────────────

(defn info  [msg] (println (str CYAN  "[*]"  RESET " " msg)))
(defn ok    [msg] (println (str GREEN "[OK]" RESET " " msg)))
(defn warn  [msg] (println (str YELLOW "[!]" RESET " " msg)))
(defn error [msg] (println (str RED   "[X]"  RESET " " msg)))

(defn divider []
  (println (str DIM "-----------------------------------------------------" RESET)))

(defn section [title]
  (divider)
  (println (str MAGENTA DIM "  ~ " title " ~" RESET))
  (divider)
  (println))

;; ── Prompt Helpers ────────────────────────────────────────────────────────────

(defn prompt
  "Print a [?] prompt and read a line. Returns `default` if input is blank."
  [msg default]
  (print (str BOLD CYAN "[?]" RESET " " msg
              (when default (str " [" default "]"))
              ": "))
  (flush)
  (let [line (str/trim (or (read-line) ""))]
    (if (str/blank? line) default line)))

(defn confirm
  "Ask a Y/n question. Returns true unless the user types 'n'."
  [msg]
  (print (str CYAN "[?]" RESET " " msg " (Y/n): "))
  (flush)
  (let [line (str/lower-case (or (read-line) ""))]
    (not= (str/trim line) "n")))

;; ── Process Helpers ───────────────────────────────────────────────────────────

(defn cmd-output
  "Run a command and return its stdout as a trimmed string, or nil on failure."
  [& cmd]
  (try
    (let [result @(proc/process (vec cmd) {:out :string :err :string})]
      (when (zero? (:exit result))
        (str/trim (:out result))))
    (catch Exception _ nil)))

(defn cmd-available?
  "Check whether a command exists on PATH."
  [cmd]
  (some? (cmd-output cmd "--version")))

(defn run-proc!
  "Run a command, streaming output to the terminal. Ignores errors."
  [& cmd]
  (try @(proc/process (vec cmd))
       (catch Exception _ nil)))

(defn open-url
  "Open a URL in the system default browser."
  [url]
  (cond
    windows? (run-proc! "cmd" "/c" "start" url)
    mac?     (run-proc! "open" url)
    :else    (run-proc! "xdg-open" url)))

;; ── Config File Loader ────────────────────────────────────────────────────────

(defn load-conf
  "Parse a simple key=value conf file, ignoring comments and blank lines."
  [path]
  (try
    (->> (str/split-lines (slurp path))
         (remove #(or (str/blank? %) (str/starts-with? (str/trim %) ";")))
         (filter #(str/includes? % "="))
         (map (fn [line]
                (let [[k v] (str/split line #"=" 2)]
                  [(str/trim k) (str/trim (or v ""))])))
         (into {}))
    (catch Exception _ {})))

;; ── Banner ────────────────────────────────────────────────────────────────────

(defn print-banner []
  (println)
  (divider)
  (println (str MAGENTA BOLD "  * T H E   S P E L L B O O K  *" RESET))
  (println (str MAGENTA DIM "        Installation Ritual — Cross-Platform Edition" RESET))
  (println)
  (println (str DIM "  Another wizard stands before you, robes singed from the journey." RESET))
  (println (str DIM "  They carry the Spellbook — sealed, awaiting your worthy hand." RESET))
  (println (str DIM "  Answer truthfully, and the arcane directories shall be conjured." RESET))
  (divider)
  (println))

;; =============================================================================
;;  PHASE 1 — WHERE TO INSTALL
;; =============================================================================

(defn detect-onedrive
  "On Windows, scan common OneDrive/Documents locations. Returns path or nil."
  []
  (when windows?
    (let [profile (System/getenv "USERPROFILE")
          od-env  (System/getenv "ONEDRIVE")]
      (some (fn [candidate]
              (when (and candidate (fs/exists? candidate))
                (str candidate)))
            [(when od-env  (p od-env "Documents"))
             (when profile (p profile "OneDrive" "Documents"))
             (when profile
               (let [matches (fs/glob profile "OneDrive - */Documents")]
                 (when (seq matches) (str (first matches)))))]))))

;; ── Already-installed guard ───────────────────────────────────────────────────

(defn already-installed?
  "Returns true if spellbook.conf already exists at the given directory,
  indicating a prior installation."
  [install-dir]
  (fs/exists? (p install-dir "spellbook.conf")))

(defn phase-location [conf-map]
  (section "Phase I: Choosing the Land")
  (println (str DIM "  Every great library needs a home. Choose wisely — the spirits" RESET))
  (println (str DIM "  of organisation are particular about where they dwell." RESET))
  (println)
  (let [conf-dir   (get conf-map "install_dir")
        onedrive   (detect-onedrive)
        local-docs (p (home-dir) "Documents" "spellbook")]
    (if conf-dir
      (expand-path conf-dir)
      (if onedrive
        (let [od-spellbook (p onedrive "spellbook")]
          (info (str "OneDrive detected at: " onedrive))
          (println (str DIM "  A cloud-tethered realm has been found. The Spellbook may dwell" RESET))
          (println (str DIM "  there, or remain grounded on local stone." RESET))
          (println)
          (println "  Where would you like to install the Spellbook?")
          (println)
          (println (str "  1)  Local Documents    (" local-docs ")"))
          (println (str "  2)  OneDrive Documents (" od-spellbook ")"))
          (println "  3)  Custom path")
          (println)
          (case (prompt "Choice" "1")
            "2" (do (ok "The cloud realm is chosen. May your connection never waver.") od-spellbook)
            "3" (expand-path (prompt "Enter full install path" nil))
            (do (ok "Local stone it is. Solid, dependable, yours alone.") local-docs)))
        (do
          (info "No cloud realm detected. The Spellbook shall root itself locally.")
          (println (str DIM "  Your Documents folder awaits, patient and unassuming." RESET))
          (println)
          (println (str "  1)  Default  (" local-docs ")"))
          (println "  2)  Custom path")
          (println)
          (if (= "2" (prompt "Choice" "1"))
            (expand-path (prompt "Enter full install path" nil))
            local-docs))))))

;; =============================================================================
;;  PHASE 2 — DEPENDENCIES
;; =============================================================================


;; ── Ollama ────────────────────────────────────────────────────────────────────

(defn check-ollama [conf-map]
  (println (str MAGENTA DIM "  ~ Will you commune with a local spirit or a distant one?  ~" RESET))
  (println (str DIM "  The Spellbook speaks through an oracle called Ollama. It may" RESET))
  (println (str DIM "  reside on this machine, or on a server elsewhere on your network." RESET))
  (println)
  (let [default-host (or (get conf-map "ollama_host") "127.0.0.1:11434")]
    (println "  1) Local  (Ollama runs on this machine)")
    (println "  2) Remote (Ollama runs on another server)")
    (println)
    (case (prompt "Choice" "1")
      "2"
      (let [host (prompt "Remote Ollama host (ip:port)" default-host)]
        (ok (str "Remote Ollama host: " host))
        (println)
        host)

      ;; default: local
      (do
        (if (cmd-available? "ollama")
          (ok "Ollama is already installed.")
          (do (warn "Ollama not found.")
              (info "Download Ollama from: https://ollama.com/download")
              (when (confirm "Open the Ollama download page now?")
                (open-url "https://ollama.com/download"))
              (info "Install Ollama, then continue or rerun this wizard.")))
        (println)
        default-host))))

;; ── Model selection ───────────────────────────────────────────────────────────

(defn choose-model [conf-map]
  (let [default-model (or (get conf-map "ollama_model") "granite4:3b")]
    (println)
    (println (str MAGENTA DIM "  ~ Which spirit shall inhabit the Spellbook's mind?  ~" RESET))
    (println (str DIM "  Each model is a different familiar — some swift and nimble," RESET))
    (println (str DIM "  others deep and deliberate. Choose the one that suits your craft." RESET))
    (println)
    (println "  Suggested models (must be pulled in Ollama first):")
    (println (str DIM "    cogito:8b   — thoughtful, strong instruction-following; recommended" RESET))
    (println (str DIM "    granite4:3b — swift and light, well-suited for tagging" RESET))
    (println (str DIM "    llama3.1:8b — a reliable generalist" RESET))
    (println)
    (let [model (prompt "Ollama model name" default-model)]
      (ok (str "Model set to: " model))
      (println)
      model)))

;; =============================================================================
;;  PHASE 3 — BUILD THE SPELLBOOK
;; =============================================================================

(defn make-dir [path]
  (if (fs/exists? path)
    (info (str "Exists  : " path))
    (do (fs/create-dirs path)
        (ok  (str "Created : " path)))))

(defn write-conf [install-dir ollama-host ollama-model]
  (println (str MAGENTA DIM "  ~ Inscribing the Spellbook configuration tome...  ~" RESET))
  (println)
  (let [conf-out (p install-dir "spellbook.conf")
        now      (java.time.LocalDate/now)
        sep      (if windows? "\\" "/")
        lines    ["; +============================================================+"
                  "; |           * S P E L L B O O K . C O N F  * |"
                  (str "; |       Generated by Install Wizard on " now "              |")
                  "; +============================================================+"
                  ""
                  "[alias]"
                  "contacts = people"
                  "tasks    = todo"
                  ""
                  "[commands]"
                  "; Move a file to the journal directory"
                  (str "journal = mv $filename content" sep "journal")
                  ""
                  "[tags]"
                  "; ── Core Personal ─────────────────────────────────────────────"
                  "contacts" "events" "todo" "email" "communication"
                  "calendar" "alarm" "journal" "note" "datum" "name"
                  "; ── Crafts & Trades ────────────────────────────────────────────"
                  "tailoring" "agriculture" "architecture" "martial-arts" "trade"
                  "cooking" "metallurgy" "musical-instrument" "strategy-game"
                  "calligraphy" "Chinese-painting"
                  "; ── Trivium ───────────────────────────────────────────────────"
                  "rhetoric" "grammar" "logic"
                  "; ── Quadrivium ────────────────────────────────────────────────"
                  "astronomy" "arithmetic" "geometry" "music"
                  "; ── Academic Disciplines ──────────────────────────────────────"
                  "anthropology" "English" "literature" "fine-arts" "philosophy"
                  "psychology" "sociology" "journalism" "economics" "law"
                  "communications" "creative-arts" "art" "history"
                  "formal-science" "natural-science" "technology"
                  "; ── Life Areas ────────────────────────────────────────────────"
                  "personal" "work"
                  ""
                  "[spellbook]"
                  (str "root          = " install-dir)
                  (str "inbox         = " (p install-dir "inbox"))
                  (str "archive       = " (p install-dir "content" "archive"))
                  (str "notes         = " (p install-dir "content" "notes"))
                  (str "journal       = " (p install-dir "content" "journal"))
                  (str "maps          = " (p install-dir "content" "maps"))
                  (str "taghub        = " (p install-dir "content" "maps" "tag-hub"))
                  (str "wiki          = " (p install-dir "content" "maps" "wiki"))
                  (str "hubs          = " (p install-dir "content" "maps" "hubs"))
                  (str "backlinks     = " (p install-dir "content" "maps" "backlinks"))
                  (str "scripts       = " (p install-dir "infrastructure" "scripts"))
                  (str "documentation = " (p install-dir "infrastructure" "documentation"))
                  (str "rituals       = " (p install-dir "infrastructure" "rituals"))
                  (str "ollama_host   = " ollama-host)
                  (str "ollama_model  = " ollama-model)
                  "plugin_sigil  ="
                  ""
                  "; Rituals registered explicitly by name=path."
                  "; These override any same-named .ritual file in the rituals/ directory."
                  "[rituals]"
                  (str "sleep         = " (p install-dir "infrastructure" "rituals" "sleep.ritual"))
                  (str "reset         = " (p install-dir "infrastructure" "rituals" "reset.ritual"))
                  (str "query         = " (p install-dir "infrastructure" "rituals" "query.ritual"))
                  (str "wiki          = " (p install-dir "infrastructure" "rituals" "wiki.ritual"))
                  ""
                  "[spellbook-ignored]"
                  "\"infrastructure\"" "\"projects\""
                  "\"archive\"" "\"assets\"" "\"maps\""]]
    (spit conf-out (str/join "\n" lines))
    (ok (str "spellbook.conf written to: " conf-out))
    (println)
    conf-out))

;; ── Source directories (relative to this installer script) ───────────────────

(def installer-dir  (str (fs/parent (fs/absolutize *file*))))
(def scripts-src    installer-dir)
(def rituals-src    (p (fs/parent installer-dir) "rituals"))

;; ── Dynamic file discovery ────────────────────────────────────────────────────
;;
;;  Discovers installable files at runtime — no hardcoded lists.
;;  Scripts: .py / .clj / .sh in infrastructure/scripts/ (excludes this installer).
;;  Rituals: .ritual files in infrastructure/rituals/.
;;  Directories named old/, export/, or __pycache__/ are skipped, as are the
;;  platform-specific bb binaries (bb-linux, bb-mac).

(def ^:private excluded-dirs  #{"old" "export" "__pycache__"})
(def ^:private excluded-files #{"bb-linux" "bb-mac"})

(defn discover-scripts []
  (if-let [manifest (io/resource "scripts/MANIFEST")]
    (->> (str/split-lines (slurp manifest)) (remove str/blank?) sort)
    (->> (fs/list-dir scripts-src)
         (remove #(and (fs/directory? %)
                       (excluded-dirs (str (fs/file-name %)))))
         (filter fs/regular-file?)
         (map #(str (fs/file-name %)))
         (remove excluded-files)
         (filter #(and (or (str/ends-with? % ".py")
                           (str/ends-with? % ".sh")
                           (str/ends-with? % ".clj"))
                       (not= % "install_spellbook.clj")))
         sort)))

(defn discover-rituals []
  (if-let [manifest (io/resource "rituals/MANIFEST")]
    (->> (str/split-lines (slurp manifest)) (remove str/blank?) sort)
    (->> (fs/list-dir rituals-src)
         (remove #(and (fs/directory? %)
                       (excluded-dirs (str (fs/file-name %)))))
         (filter fs/regular-file?)
         (map #(str (fs/file-name %)))
         (remove excluded-files)
         (filter #(str/ends-with? % ".ritual"))
         sort)))

(defn install-scripts
  "Copies scripts into the new installation.
  Sources from classpath resources when running from EXE, filesystem otherwise.
  Shell scripts (.sh) are made executable on Unix/Mac."
  [install-dir]
  (println (str MAGENTA DIM "  ~ Transcribing the arcane scripts into the grimoire...  ~" RESET))
  (println)
  (let [scripts-dir  (p install-dir "infrastructure" "scripts")
        script-names (discover-scripts)
        installed    (atom 0)]
    (doseq [script-name script-names]
      (let [dest (java.io.File. (p scripts-dir script-name))]
        (if-let [res (io/resource (str "scripts/" script-name))]
          (with-open [in (.openStream res)] (io/copy in dest))
          (fs/copy (p scripts-src script-name) dest {:replace-existing true}))
        (when (and (not windows?) (str/ends-with? script-name ".sh"))
          (.setExecutable dest true))
        (ok (str "Installed : " script-name))
        (swap! installed inc)))
    (println)
    (ok (str "All " @installed " scripts installed to: " scripts-dir))
    (println)))

(defn install-rituals
  "Copies rituals into the new installation.
  Sources from classpath resources when running from EXE, filesystem otherwise."
  [install-dir]
  (println (str MAGENTA DIM "  ~ Binding the ritual scrolls into the grimoire...  ~" RESET))
  (println)
  (let [rituals-dir  (p install-dir "infrastructure" "rituals")
        ritual-names (discover-rituals)
        installed    (atom 0)]
    (doseq [ritual-name ritual-names]
      (let [dest (java.io.File. (p rituals-dir ritual-name))]
        (if-let [res (io/resource (str "rituals/" ritual-name))]
          (with-open [in (.openStream res)] (io/copy in dest))
          (fs/copy (p rituals-src ritual-name) dest {:replace-existing true}))
        (ok (str "Installed : " ritual-name))
        (swap! installed inc)))
    (println)
    (ok (str "All " @installed " rituals installed to: " rituals-dir))
    (println)))

(defn phase-build [install-dir ollama-host ollama-model]
  (section "Phase III: Conjuring the Directory Structure")
  (println (str DIM "  The ritual circle must be drawn. Each chamber serves a purpose," RESET))
  (println (str DIM "  though in time, as your mastery grows, you may reshape the layout" RESET))
  (println (str DIM "  to better suit your own craft." RESET))
  (println)
  (info "The following structure will be created under:")
  (println (str BOLD "         " install-dir RESET))
  (println)
  (doseq [line ["        inbox/"
                "        content/"
                "          notes/"
                "          archive/"
                "          assets/"
                "          journal/"
                "          maps/"
                "            backlinks/"
                "            hubs/"
                "            tag-hub/"
                "            wiki/"
                "        infrastructure/"
                "          documentation/"
                "          rituals/"
                "          scripts/"
                "        projects/"]]
    (println line))
  (println)

  (if-not (confirm "Shall the wizard conjure this mind palace now?")
    (do (error "The ritual was abandoned. No directories were created.") nil)
    (do
      (doseq [d [(p install-dir)
                 (p install-dir "inbox")
                 (p install-dir "content" "archive")
                 (p install-dir "content" "assets")
                 (p install-dir "content" "journal")
                 (p install-dir "content" "maps" "backlinks")
                 (p install-dir "content" "maps" "hubs")
                 (p install-dir "content" "maps" "wiki")
                 (p install-dir "content" "notes")
                 (p install-dir "content" "maps" "tag-hub")
                 (p install-dir "infrastructure" "documentation")
                 (p install-dir "infrastructure" "rituals")
                 (p install-dir "infrastructure" "scripts")
                 (p install-dir "projects")]]
        (make-dir d))
      (println)
      (let [conf-out (write-conf install-dir ollama-host ollama-model)]
        (install-scripts install-dir)
        (install-rituals install-dir)
        conf-out))))


;; ── Summary ───────────────────────────────────────────────────────────────────

(defn print-summary [install-dir conf-out ollama-host ollama-model]
  (divider)
  (println)
  (println (str MAGENTA BOLD "  * The enchantment is complete! The Spellbook lives.  *" RESET))
  (println)
  (println (str DIM "  Guard the configuration tome well, for it binds the Spellbook" RESET))
  (println (str DIM "  to this machine. Should you ever need to move or reconfigure it," RESET))
  (println (str DIM "  that is where you shall begin." RESET))
  (println)
  (info (str "Installed at    : " install-dir))
  (info (str "Configuration   : " conf-out))
  (info (str "Scripts         : " (p install-dir "infrastructure" "scripts")))
  (info (str "Ollama host     : " ollama-host))
  (info (str "Ollama model    : " ollama-model))
  (println)
  (println (str MAGENTA DIM "  ~ Open Obsidian and point your vault at the install directory.  ~" RESET))
  (println (str MAGENTA DIM "  ~ Drop notes into inbox/ and awaken the Spellbook with:        ~" RESET))
  (println (str MAGENTA DIM "  ~   bb " (p install-dir "infrastructure" "scripts" "spellbook.clj") " process ~" RESET))
  (println)
  (divider)
  (println))

;; =============================================================================
;;  ENTRY POINT
;; =============================================================================

(defn -main [& args]
  (let [conf-path (first args)
        conf-map  (cond
                    (nil? conf-path)
                    {}

                    (fs/exists? conf-path)
                    (do (info (str "Loading configuration from: " conf-path))
                        (ok "Configuration loaded.")
                        (println)
                        (load-conf conf-path))

                    :else
                    (do (warn (str "Config file not found: " conf-path
                                   " -- proceeding interactively."))
                        (println)
                        {}))]

    (print-banner)

    ;; Phase 1 — Location
    (let [install-dir (phase-location conf-map)]
      (println)
      (info "Spellbook will be installed to:")
      (println (str BOLD "         " install-dir RESET))
      (println)

      ;; Guard: abort if already installed
      (when (already-installed? install-dir)
        (println)
        (warn "A Spellbook already dwells at this location.")
        (info (str "Found: " (p install-dir "spellbook.conf")))
        (println (str DIM "  The ritual cannot be performed twice upon the same ground." RESET))
        (println (str DIM "  Remove or rename the existing installation before continuing." RESET))
        (println)
        (System/exit 1))

      (when-not (confirm "Proceed with this location?")
        (error "Very well. Seek a more suitable land and try again.")
        (System/exit 0))
      (ok "Location confirmed. The ritual may begin.")
      (println)

      ;; Phase 2 — Dependencies
      (section "Phase II: Gathering the Ingredients")
      (let [ollama-host  (check-ollama conf-map)
            ollama-model (choose-model conf-map)]

        ;; Phase 3 — Build
        (let [conf-out       (phase-build install-dir ollama-host ollama-model)
              effective-conf (or conf-out (p install-dir "spellbook.conf"))]
          (print-summary install-dir effective-conf ollama-host ollama-model)

          ;; On Windows, pause so a double-click terminal doesn't vanish
          (when windows?
            (print "Press Enter to exit...")
            (flush)
            (read-line)))))))

(when (= *file* (System/getProperty "babashka.file"))
  (apply -main *command-line-args*))
