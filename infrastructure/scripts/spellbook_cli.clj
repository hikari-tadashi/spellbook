#!/usr/bin/env bb

(ns spellbook-cli
  (:require [babashka.process :refer [process]]
            [babashka.fs :as fs]
            [clojure.string :as str]))

;; ---------------------------------------------------------------------------
;; Config Parsing
;; ---------------------------------------------------------------------------

(defn find-conf
  "Walks up from cwd looking for spellbook.conf"
  []
  (loop [dir (fs/cwd)]
    (let [candidate (fs/path dir "spellbook.conf")]
      (cond
        (fs/exists? candidate) candidate
        (or (nil? (fs/parent dir))
            (= (str dir) (str (fs/parent dir)))) (throw (ex-info (str "spellbook.conf not found.\n\n"
                                                                      "Run this script from within a spellbook project directory (or any subdirectory).\n"
                                                                      "A minimal spellbook.conf looks like:\n\n"
                                                                      "  [spellbook]\n"
                                                                      "  root    = /path/to/your/spellbook\n"
                                                                      "  rituals = infrastructure/rituals\n\n"
                                                                      "Optionally register rituals by name:\n\n"
                                                                      "  [rituals]\n"
                                                                      "  my-ritual = infrastructure/rituals/my-ritual.ritual\n") {}))
        :else (recur (fs/parent dir))))))

(defn parse-conf
  "Returns a map of {section {key value}} from an INI-style conf file.
   Keys with no '=' get a nil value."
  [conf-path]
  (first
    (reduce
      (fn [[result section] line]
        (let [line (-> line str/trim (str/split #"[#;]") first str/trim)]
          (cond
            (str/blank? line)
            [result section]

            (re-matches #"\[.+\]" line)
            [result (subs line 1 (dec (count line)))]

            section
            (let [[k v] (str/split line #"=" 2)]
              [(assoc-in result [section (str/trim k)] (some-> v str/trim)) section])

            :else [result section])))
      [{} nil]
      (str/split-lines (slurp (str conf-path))))))

;; ---------------------------------------------------------------------------
;; Ritual Discovery
;; ---------------------------------------------------------------------------

(defn load-ritual
  "Reads a .ritual file and returns a vec of non-blank, non-comment lines."
  [path]
  (->> (str/split-lines (slurp (str path)))
       (map str/trim)
       (remove #(or (str/blank? %) (str/starts-with? % "#") (str/starts-with? % ";")))))

(defn read-plugin-conf
  "Parses a plugin.conf file. Returns a map of {section {key value}},
   or nil if the file cannot be parsed or has no [plugin] section."
  [plugin-dir]
  (let [conf-path (fs/path plugin-dir "plugin.conf")]
    (when (fs/exists? conf-path)
      (let [parsed (parse-conf conf-path)]
        (when (get parsed "plugin")
          parsed)))))

(defn discover-plugins
  "Scans infrastructure/plugins/ for subdirectories containing plugin.conf.
   Returns {:rituals {name path} :components {plugin.component invocation}}.

   Collision handling:
   - Two plugins with the same [plugin] name key: warn to stderr listing both
     directory paths; the first discovered alphabetically wins.
   - Two plugins registering the same plugin.component key: warn to stderr
     listing both; the first discovered alphabetically wins.
   Alphabetical ordering is enforced explicitly to ensure determinism."
  [conf-path]
  (let [conf-dir      (fs/parent conf-path)
        plugins-dir   (fs/path conf-dir "infrastructure" "plugins")]
    (if-not (fs/exists? plugins-dir)
      {:rituals {} :components {}}
      (let [plugin-dirs (->> (fs/list-dir plugins-dir)
                             (filter fs/directory?)
                             (sort-by str))]
        (reduce
          (fn [acc plugin-dir]
            (let [plugin-conf (read-plugin-conf plugin-dir)]
              (if-not plugin-conf
                acc
                (let [plugin-name   (get-in plugin-conf ["plugin" "name"])
                      rituals-rel   (get-in plugin-conf ["plugin" "rituals"])
                      rituals-dir   (if (not (str/blank? rituals-rel))
                                      (fs/path plugin-dir rituals-rel)
                                      plugin-dir)
                      new-rituals   (if (fs/exists? rituals-dir)
                                      (into {}
                                        (for [f    (fs/list-dir rituals-dir)
                                              :let  [fname (str (fs/file-name f))]
                                              :when (str/ends-with? fname ".ritual")]
                                          [(str/replace fname #"\.ritual$" "") f]))
                                      {})
                      components    (get plugin-conf "components" {})
                      new-components (into {}
                                      (for [[cname invocation] components
                                            :when (and cname invocation)]
                                        (let [key      (str plugin-name "." cname)
                                              resolved (str/replace
                                                         invocation
                                                         #"(\S+\.(?:py|sh|clj|rb|js|ts))"
                                                         (fn [[_ p]]
                                                           (str (fs/relativize
                                                                  conf-dir
                                                                  (fs/path plugin-dir p)))))]
                                          [key resolved])))]
                  (doseq [[rname _] new-rituals]
                    (when (contains? (:rituals acc) rname)
                      (binding [*out* *err*]
                        (println (str "Warning: ritual name collision '" rname
                                      "' between plugins. "
                                      "First discovered (alphabetically) wins. "
                                      "Override via [rituals] in spellbook.conf.")))))
                  (doseq [[ckey _] new-components]
                    (when (contains? (:components acc) ckey)
                      (binding [*out* *err*]
                        (println (str "Warning: component key collision '" ckey
                                      "' between plugins. "
                                      "First discovered (alphabetically) wins.")))))
                  {:rituals    (merge new-rituals    (:rituals    acc))
                   :components (merge new-components (:components acc))}))))
          {:rituals {} :components {}}
          plugin-dirs)))))

(defn discover-rituals
  "Returns a map of {ritual-name ritual-path}.
   Sources (in increasing priority):
     1. plugin rituals (lowest priority)
     2. .ritual files in the directory set by rituals= under [spellbook]
     3. explicit name=path entries under [rituals] in the conf"
  [conf-path conf plugin-rituals]
  (let [conf-dir    (fs/parent conf-path)

        ;; Source 2: rituals= directory under [spellbook]
        rituals-dir (get-in conf ["spellbook" "rituals"])
        from-dir    (if rituals-dir
                      (let [dir (fs/path conf-dir rituals-dir)]
                        (if (fs/exists? dir)
                          (into {}
                            (for [f     (fs/list-dir dir)
                                  :let  [fname (str (fs/file-name f))]
                                  :when (str/ends-with? fname ".ritual")]
                              [(str/replace fname #"\.ritual$" "") f]))
                          (do (println (str "Warning: rituals dir not found: " dir)) {})))
                      {})

        ;; Source 3: explicit [rituals] section in conf
        from-conf   (into {}
                      (for [[name rel-path] (get conf "rituals" {})
                            :when rel-path]
                        [name (fs/path conf-dir rel-path)]))]

    ;; plugin-rituals < from-dir < from-conf
    (merge plugin-rituals from-dir from-conf)))

(defn expand-components
  "Expands plugin.component tokens in a ritual line using the component registry.

   Sigil behaviour:
   - If plugin-sigil is nil or blank: every whitespace-delimited token that
     matches a registry key is expanded.
   - If plugin-sigil is set: only tokens beginning with that character are
     candidates; the sigil is stripped before the registry lookup.

   Path guard: if a token (after sigil stripping) resolves to an existing
   file path from the working directory, it is NOT expanded."
  [line component-registry plugin-sigil]
  (if (empty? component-registry)
    line
    (let [use-sigil? (not (str/blank? plugin-sigil))
          sigil-char (when use-sigil? (str (first plugin-sigil)))]
      (str/join " "
        (map (fn [token]
               (let [candidate? (if use-sigil?
                                  (str/starts-with? token sigil-char)
                                  (and (str/includes? token ".")
                                       (not (str/includes? token "/"))
                                       (not (str/includes? token "\\"))))
                     bare       (if (and use-sigil? candidate?)
                                  (subs token (count sigil-char))
                                  token)]
                 (if (and candidate?
                          (contains? component-registry bare)
                          (not (fs/exists? bare)))
                   (get component-registry bare)
                   token)))
             (str/split line #"\s+"))))))

;; ---------------------------------------------------------------------------
;; Ritual Execution
;; ---------------------------------------------------------------------------

(def shell-args
  "Shell invocation prefix for the current OS. Enables pipes and redirects in ritual commands."
  (if (str/starts-with? (System/getProperty "os.name") "Windows")
    ["cmd" "/c"]
    ["sh" "-c"]))

(defn run-ritual!
  "Runs a named ritual from a ritual path. Returns exit code (0 = success).
   extra-args, if provided, are appended to each command in the ritual."
  [name ritual-path working-dir component-registry plugin-sigil & [extra-args]]
  (let [commands  (vec (load-ritual ritual-path))
        args-str  (when (seq extra-args) (str " " (str/join " " extra-args)))]
    (if (empty? commands)
      (do (println (str "ritual '" name "' has no commands.")) 1)
      (do
        (println (str "▶ " name))
        (loop [[cmd & rest-cmds] commands step 0]
          (if-not cmd
            (do (println "✓ Done.") 0)
            (let [expanded (expand-components cmd component-registry plugin-sigil)
                  full-cmd (str expanded args-str)
                  exit     (:exit @(apply process {:dir (str working-dir) :out :inherit :err :inherit} (conj shell-args full-cmd)))]
              (if (= 0 exit)
                (recur rest-cmds (inc step))
                (do
                  (println (str "✗ Ritual '" name "' failed at step " step " (exit " exit ")"))
                  exit)))))))))

;; ---------------------------------------------------------------------------
;; Main
;; ---------------------------------------------------------------------------

(defn list-rituals! [rituals]
  (if (empty? rituals)
    (println "No rituals found. Add a [rituals] section to spellbook.conf\nor set rituals= under [spellbook] pointing to a directory of .ritual files.")
    (do
      (println "Available rituals:")
      (doseq [name (sort (keys rituals))]
        (println (str "  " name))))))

;; ---------------------------------------------------------------------------
;; First-run menu (no spellbook.conf found)
;; ---------------------------------------------------------------------------

(defn first-run-menu! []
  (println)
  (println "No spellbook.conf found.")
  (println)
  (println "  1) Fresh install  — create a new Spellbook (directories + spellbook.conf)")
  (println "  2) Minimal setup  — write a spellbook.conf for an existing directory")
  (println "  3) Exit")
  (println)
  (print "[?] Choice [1]: ")
  (flush)
  (let [choice (str/trim (or (read-line) ""))]
    (case (if (str/blank? choice) "1" choice)
      "2" (do (try (require '[create-conf])
                   (catch Exception _
                     (load-file (str (fs/parent *file*) "/create_conf.clj"))))
              ((resolve 'create-conf/-main))
              (System/exit 0))
      "3" (System/exit 0)
      (do (try (require '[install-spellbook])
               (catch Exception _
                 (load-file (str (fs/parent *file*) "/install_spellbook.clj"))))
          ((resolve 'install-spellbook/-main))
          (System/exit 0)))))

;; ---------------------------------------------------------------------------
;; Main
;; ---------------------------------------------------------------------------

(defn -main [& args]
  (let [[cmd & extra-args] args]
    (if (= cmd "install")
      ;; "install" is always handled directly — warn if an existing conf is nearby
      (do
        (when-let [existing (try (find-conf) (catch Exception _ nil))]
          (println (str "[!] Note: a spellbook.conf was already found at " (str existing)))
          (println "    You can proceed to create a new installation at a different location."))
        (try (require '[install-spellbook])
             (catch Exception _
               (load-file (str (fs/parent *file*) "/install_spellbook.clj"))))
        ((resolve 'install-spellbook/-main))
        (System/exit 0))
      ;; Normal flow: walk up dirs for a conf
      (let [conf-path (try (find-conf) (catch Exception _ nil))]
        (if (nil? conf-path)
          (first-run-menu!)
          (let [conf         (parse-conf conf-path)
                working-dir  (fs/parent conf-path)
                plugins      (discover-plugins conf-path)
                plugin-sigil (get-in conf ["spellbook" "plugin_sigil"] "")
                rituals      (discover-rituals conf-path conf (:rituals plugins))
                components   (:components plugins)]
            (cond
              (or (nil? cmd) (= cmd "list"))
              (list-rituals! rituals)

              :else
              (if-let [ritual-path (get rituals cmd)]
                (System/exit (run-ritual! cmd ritual-path working-dir components plugin-sigil extra-args))
                (do
                  (println (str "Unknown ritual: '" cmd "'"))
                  (list-rituals! rituals)
                  (System/exit 1))))))))))

;; Support direct `bb spellbook_cli.clj` invocation alongside uberjar -main dispatch.
(when (= *file* (System/getProperty "babashka.file"))
  (apply -main *command-line-args*))
