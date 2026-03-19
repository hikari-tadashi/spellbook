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

(defn discover-rituals
  "Returns a map of {ritual-name ritual-path}.
   Sources (in increasing priority):
     1. .ritual files in the directory set by rituals= under [spellbook]
     2. explicit name=path entries under [rituals] in the conf"
  [conf-path conf]
  (let [conf-dir    (fs/parent conf-path)

        ;; Source 1: rituals= directory under [spellbook]
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

        ;; Source 2: explicit [rituals] section in conf
        from-conf   (into {}
                      (for [[name rel-path] (get conf "rituals" {})
                            :when rel-path]
                        [name (fs/path conf-dir rel-path)]))]

    ;; conf entries override dir-based ones on name collision
    (merge from-dir from-conf)))

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
  [name ritual-path working-dir & [extra-args]]
  (let [commands  (vec (load-ritual ritual-path))
        args-str  (when (seq extra-args) (str " " (str/join " " extra-args)))]
    (if (empty? commands)
      (do (println (str "ritual '" name "' has no commands.")) 1)
      (do
        (println (str "▶ " name))
        (loop [[cmd & rest-cmds] commands step 0]
          (if-not cmd
            (do (println "✓ Done.") 0)
            (let [full-cmd (str cmd args-str)
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
      "2" (do (require '[create-conf])
              ((resolve 'create-conf/-main))
              (System/exit 0))
      "3" (System/exit 0)
      (do (require '[install-spellbook])
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
        (require '[install-spellbook])
        ((resolve 'install-spellbook/-main))
        (System/exit 0))
      ;; Normal flow: walk up dirs for a conf
      (let [conf-path (try (find-conf) (catch Exception _ nil))]
        (if (nil? conf-path)
          (first-run-menu!)
          (let [conf        (parse-conf conf-path)
                working-dir (fs/parent conf-path)
                rituals     (discover-rituals conf-path conf)]
            (cond
              (or (nil? cmd) (= cmd "list"))
              (list-rituals! rituals)

              :else
              (if-let [ritual-path (get rituals cmd)]
                (System/exit (run-ritual! cmd ritual-path working-dir extra-args))
                (do
                  (println (str "Unknown ritual: '" cmd "'"))
                  (list-rituals! rituals)
                  (System/exit 1))))))))))

;; Support direct `bb spellbook_cli.clj` invocation alongside uberjar -main dispatch.
(when (= *file* (System/getProperty "babashka.file"))
  (apply -main *command-line-args*))
