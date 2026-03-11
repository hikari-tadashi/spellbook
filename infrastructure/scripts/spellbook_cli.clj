#!/usr/bin/env bb

(require '[babashka.process :refer [process]]
         '[babashka.fs :as fs]
         '[clojure.string :as str])

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
        (= (str dir) (str (fs/parent dir))) (throw (ex-info "spellbook.conf not found" {}))
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
  "Runs a named ritual from a ritual path. Returns exit code (0 = success)."
  [name ritual-path working-dir]
  (let [commands (vec (load-ritual ritual-path))]
    (if (empty? commands)
      (do (println (str "ritual '" name "' has no commands.")) 1)
      (do
        (println (str "▶ " name))
        (loop [[cmd & rest-cmds] commands step 0]
          (if-not cmd
            (do (println "✓ Done.") 0)
            (let [exit (:exit @(apply process {:dir (str working-dir) :out :inherit :err :inherit} (conj shell-args cmd)))]
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

(let [conf-path   (find-conf)
      conf        (parse-conf conf-path)
      working-dir (fs/parent conf-path)
      rituals     (discover-rituals conf-path conf)
      [cmd & _]   *command-line-args*]
  (cond
    (or (nil? cmd) (= cmd "list"))
    (list-rituals! rituals)

    :else
    (if-let [ritual-path (get rituals cmd)]
      (System/exit (run-ritual! cmd ritual-path working-dir))
      (do
        (println (str "Unknown ritual: '" cmd "'"))
        (list-rituals! rituals)
        (System/exit 1)))))
