#!/usr/bin/env python3
"""Build data/structure.json: rules that hint which pandas AREA label an issue belongs to.

The rules are learned from earlier issues that pandas maintainers already labelled,
then checked on later issues, so every rule comes with evidence you can report.

  1. Vocabulary: public function, method and class names defined in your pandas clone
     (at the commit pinned in UPSTREAM.md), plus accessors such as .str and .dt.
  2. Signals in an issue: pandas names in its title or body, and pandas file paths from
     tracebacks (with their parent folders).
  3. Training issues: corpus issues created BEFORE your earliest test case that a
     maintainer has triaged ("Needs Triage" removed). Test cases are always left out.
  4. A signal becomes a rule for a label when at least MIN_HITS training issues with the
     signal had the label, and at least MIN_PRECISION of all training issues with it did.
  5. Each rule is then checked on triaged issues created on or after the cutoff (still
     without test cases). Results are printed and saved in structure.json.

Run from your sandbox repo root, after build_corpus.py:

    python tools/snapshots/build_structure.py --list-labels   # counts, to choose AREA_LABELS
    python tools/snapshots/build_structure.py                 # build rules and report

Needs the GitHub CLI (to confirm the labels exist) and your local pandas clone.
"""
import argparse
import ast
import json
import re
import subprocess
import sys
from collections import Counter, defaultdict
from pathlib import Path

PANDAS = Path("../pandas")                # top folder of your pandas clone (outside this repo)
CORPUS = Path("data/issues_corpus.json")
OUT = Path("data/structure.json")

# Upstream issue numbers of ALL your test cases (golden, no-action and adversarial).
# They are never used to learn rules, and the earliest one's date is the cutoff.
TEST_CASE_ISSUES = set({70991, 67726, 71275, 64253, 63757, 63269, 63271, 63277, 64298, 70748, 65834})

# Area labels to learn rules for: use the same names as the add-labels allowlist in your
# workflow. Run with --list-labels to see how often each label is used.
AREA_LABELS = [
    "Strings", "Arrow", "IO XML", "Reshaping", "Visualization","IO CSV", "expressions", "IO Parquet"
]

MIN_HITS_KEYWORD = 5      # training issues that had the name AND the label
MIN_HITS_PATH = 3         # tracebacks are rarer than names, so a lower bar
MIN_PRECISION = 0.6       # share of training issues with the signal that had the label
MAX_RULES_PER_LABEL = 10

IGNORE_KEYWORDS = set()   # names you never want as rules, e.g. {"DataFrame"}
MANUAL_RULES = []         # rules you add by hand; they are checked and reported like the rest
# e.g. [{"kind": "keyword", "match": "read_stata", "label": "IO Stata"}]

NOT_TRIAGED = "Needs Triage"
ACCESSORS = {"str", "dt", "cat", "sparse", "plot", "style", "list", "struct"}

# How a rule matches an issue. Saved into structure.json so the script that gives the
# agent its hints at run time matches issues exactly the way the rules were learned.
IDENTIFIER_RE = r"[A-Za-z_][A-Za-z0-9_]*"
PATH_RE = r"pandas[\\/]+(?:[\w.-]+[\\/]+)*[\w.-]+\.(?:py|pyx|pyi)"   # same as build_corpus.py
MATCHING = {
    "identifier_regex": IDENTIFIER_RE,
    "path_regex": PATH_RE,
    "keyword_rule": ("matches when the name is one of the identifiers found in the title or "
                     "body, after removing text that matches path_regex"),
    "path_rule": ("matches when a pandas path found in the body (runs of / or \\ turned into one /, "
                  "text before the last 'pandas/' removed) equals the rule, or starts with it "
                  "when the rule is a folder ending in /"),
}


# ---------- matching (copy these three functions into your run-time hint script) ----------

def find_names(text, vocabulary):
    """pandas names (whole identifiers) in the text. File paths are removed first, so
    'pandas/core/reshape/pivot.py' counts as a path, not as the names 'reshape' and 'pivot'."""
    text = re.sub(PATH_RE, " ", text)
    return {token for token in re.findall(IDENTIFIER_RE, text) if token in vocabulary}


def find_paths(text):
    """pandas file paths in the text, normalised to 'pandas/...' with / separators."""
    found = set()
    for raw in re.findall(PATH_RE, text):
        path = re.sub(r"[\\/]+", "/", raw)
        found.add(path[path.rfind("pandas/"):])
    return found


def rule_matches(rule, names, paths):
    if rule["kind"] == "keyword":
        return rule["match"] in names
    folder = rule["match"].endswith("/")
    return any(p == rule["match"] or (folder and p.startswith(rule["match"])) for p in paths)


# ---------- building ----------

def run(*cmd):
    # gh and git print UTF-8; say so explicitly, or Windows decodes it as cp1252
    return subprocess.run(cmd, check=True, capture_output=True, text=True, encoding="utf-8").stdout


def real_labels():
    out = run("gh", "label", "list", "-R", "pandas-dev/pandas", "--limit", "500", "--json", "name")
    return {item["name"] for item in json.loads(out)}


def pandas_vocabulary(root):
    """Public def/class names in the pandas package (tests skipped) plus accessors.

    Why: issue text is full of words that are not pandas names (df, x, print, foo,
    'the'). Only names from this set can become keyword rules, so the noise never
    gets counted. Example result: {'read_csv', 'groupby', 'pivot_table', 'Timestamp', ...}
    """
    # Accessors (s.str..., s.dt...) are created in pandas by assignment, e.g.
    # `str = Accessor("str", StringMethods)`, not with `def`, so the loop below would
    # miss them. Start the set with them.
    names = set(ACCESSORS)

    # rglob("*") lists every file and folder under <clone>/pandas, at any depth.
    # sorted() just makes the order the same on every run and every computer.
    for path in sorted((root / "pandas").rglob("*")):
        # Keep only Python source (.py) and type-stub (.pyi) files. Skip anything
        # inside a 'tests' folder: test functions (test_read_csv_bad_encoding, ...)
        # are not names users write in issues. relative_to(root) makes sure a
        # folder called 'tests' ABOVE your clone does not skip everything.
        if path.suffix not in (".py", ".pyi") or "tests" in path.relative_to(root).parts:
            continue
        try:
            # ast.parse reads the file as Python code (a tree of definitions,
            # statements, ...) instead of plain text. Nothing is run or imported.
            tree = ast.parse(path.read_text(encoding="utf-8"))
        except (SyntaxError, UnicodeDecodeError, ValueError):
            # A file your Python version cannot parse is skipped, not fatal.
            continue
        # ast.walk visits every node in the tree, including methods inside classes
        # (so DataFrame.groupby gives 'groupby') and functions inside functions.
        for node in ast.walk(tree):
            if (isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef))
                    # names starting with _ are private helpers (_get_axis, ...)
                    and not node.name.startswith("_")
                    # 1-2 letter names (f, df) are too short to mean anything
                    and len(node.name) >= 3):
                names.add(node.name)

    # Remove names you chose to ignore after reading the report.
    return names - IGNORE_KEYWORDS


def path_prefixes(path):
    """'pandas/core/groupby/ops.py' -> itself, 'pandas/core/groupby/', 'pandas/core/'."""
    parts = path.split("/")
    yield path
    for i in range(len(parts) - 1, 1, -1):
        yield "/".join(parts[:i]) + "/"


def issue_signals(issue, vocabulary):
    """(names, paths) for one corpus issue."""
    text = f"{issue['title']}\n{issue.get('body_excerpt') or ''}"
    paths = set(issue["paths"]) if "paths" in issue else find_paths(text)
    return find_names(text, vocabulary), paths


def learn(train, vocabulary, root):
    """Learn rules from the training issues (triaged, created before the cutoff).

    Returns (rules, near_misses):
      rules        list of rule dicts that passed the thresholds (plus your manual rules)
      near_misses  {label: [rules that came close]}, shown in the report when a label
                   ends up with no rules, to help you write manual ones
    """
    # ---- Step 1: count -------------------------------------------------------------
    # A "signal" is something we can spot in an issue, stored as a (kind, match) pair:
    #   ("keyword", "read_csv")          the name read_csv appears in the text
    #   ("path", "pandas/io/parsers/")   a traceback path is inside that folder
    # Counter() is a dict that starts every key at 0, so `+= 1` always works.
    support = Counter()   # support[signal]       = training issues that had the signal
    hits = Counter()      # hits[(signal, label)] = ...of those, how many had the label

    for issue in train:
        names, paths = issue_signals(issue, vocabulary)

        # Turn this issue's names and paths into one SET of signals. Being a set,
        # each signal counts once per issue, however often it appears in the text.
        signals = {("keyword", n) for n in names}
        # Each path also counts as each of its parent folders, so a folder rule can be
        # learned even when issues point at different files inside it, e.g.
        # pandas/io/parsers/readers.py -> the file, pandas/io/parsers/, pandas/io/
        signals |= {("path", p) for full in paths for p in path_prefixes(full)}

        # Only the area labels we care about; Bug, Needs Info, ... are ignored here.
        labels = set(issue["labels"]) & set(AREA_LABELS)

        for signal in signals:
            support[signal] += 1                 # this issue had the signal
            for label in labels:                 # an issue with 2 area labels adds a
                hits[signal, label] += 1         # hit for each of them

    # ---- Step 2: score every (signal, label) pair that occurred at least once ------
    by_label = defaultdict(list)      # label -> rules that passed the thresholds
    near_misses = defaultdict(list)   # label -> rules that came close
    for (signal, label), h in hits.items():
        kind, match = signal
        # Precision: of all training issues with this signal, the share that had the
        # label. Example: read_csv in 30 issues, 24 of them IO CSV -> 24/30 = 0.80.
        # A name that is everywhere (DataFrame: 35 of 400 -> 0.09) scores low by itself.
        precision = h / support[signal]
        rule = {"kind": kind, "match": match, "label": label, "source": "learned",
                "train": {"hits": h, "support": support[signal], "precision": round(precision, 2)}}

        # Tracebacks are rarer than names, so path rules need fewer hits.
        need = MIN_HITS_KEYWORD if kind == "keyword" else MIN_HITS_PATH

        # A path from an old traceback may no longer exist at your pinned pandas
        # commit (file moved or deleted). Such a rule could never match, so drop it.
        if kind == "path" and not (root / match.rstrip("/")).exists():
            continue

        # The two thresholds: seen often enough (h >= need) AND reliable enough
        # (precision >= MIN_PRECISION). Requiring both stops a name seen in only 2
        # issues (2/2 = 1.0) from becoming a rule by luck.
        if h >= need and precision >= MIN_PRECISION:
            by_label[label].append(rule)
        elif h >= 2:
            near_misses[label].append(rule)

    # ---- Step 3: tidy up and keep the best rules per label --------------------------
    rules = []
    for label in AREA_LABELS:
        chosen = []
        # Sort so path rules come first, shortest (widest folder) first, then keywords.
        # A folder rule already covers every file inside it, so if
        # pandas/io/parsers/ was chosen, pandas/io/parsers/readers.py is skipped.
        for rule in sorted(by_label[label], key=lambda r: (r["kind"] != "path", len(r["match"]))):
            if rule["kind"] == "path" and any(
                    c["kind"] == "path" and rule["match"].startswith(c["match"]) for c in chosen):
                continue
            chosen.append(rule)
        # Best first: highest precision, ties broken by more hits. Then keep at most
        # MAX_RULES_PER_LABEL, so the agent's hints stay short.
        chosen.sort(key=lambda r: (-r["train"]["precision"], -r["train"]["hits"]))
        rules += chosen[:MAX_RULES_PER_LABEL]

    # ---- Step 4: add your manual rules ------------------------------------------------
    # They are added even if their numbers are weak, but with those numbers attached
    # and marked "manual", so the report shows how well they really do.
    learned = {(r["kind"], r["match"], r["label"]) for r in rules}
    for manual in MANUAL_RULES:
        if (manual["kind"], manual["match"], manual["label"]) in learned:
            print(f"Note: manual rule {manual['match']} -> {manual['label']} was learned anyway")
            continue
        signal = (manual["kind"], manual["match"])
        # Counter returns 0 for a signal never seen, so s can be 0: no precision then.
        h, s = hits[signal, manual["label"]], support[signal]
        rules.append({**manual, "source": "manual",
                      "train": {"hits": h, "support": s, "precision": round(h / s, 2) if s else None}})
    return rules, near_misses


def check(rules, issues, vocabulary):
    """Apply the rules to issues they were NOT learned from (the 'later' issues).

    This is the honest test: a rule can look good on the issues it was learned from by
    luck; how it does on newer issues is closer to how it will do on real new issues.

    Adds rule["check"] to every rule and returns a per-label summary (recall).
    """
    # Find each later issue's names and paths once, up front, instead of once per rule.
    # Each entry is (issue, names, paths); the * unpacks issue_signals' two results.
    signals = [(issue, *issue_signals(issue, vocabulary)) for issue in issues]

    # ---- Precision of each rule on the later issues --------------------------------
    for rule in rules:
        # Every later issue this rule fires on. rule_matches is the same function your
        # run-time hint script uses, so these numbers describe what the agent will see.
        matched = [i for i, names, paths in signals if rule_matches(rule, names, paths)]
        # ...and how many of them maintainers really gave the rule's label.
        # (True counts as 1 and False as 0 when summed.)
        correct = sum(rule["label"] in i["labels"] for i in matched)
        rule["check"] = {"matches": len(matched), "correct": correct,
                         # None when the rule matched nothing later: no evidence either way
                         "precision": round(correct / len(matched), 2) if matched else None}
        # Example: read_csv fired on 21 later issues, 20 had IO CSV -> precision 0.95.

    # ---- Recall of each label on the later issues ----------------------------------
    # Recall answers the opposite question: of the later issues that really HAD the
    # label, how many got at least one hint for it? The rest the agent must spot alone.
    summary = {}
    for label in AREA_LABELS:
        own = [r for r in rules if r["label"] == label]                  # this label's rules
        with_label = [(i, n, p) for i, n, p in signals if label in i["labels"]]
        # An issue counts as found if ANY of the label's rules fires on it.
        found = sum(any(rule_matches(r, n, p) for r in own) for _, n, p in with_label)
        summary[label] = {"check_issues": len(with_label), "found_by_rules": found,
                          "recall": round(found / len(with_label), 2) if with_label else None}
        # Example: 33 later issues had IO CSV, the rules found 30 -> recall 0.91.
    return summary


def load_corpus():
    if not CORPUS.exists():
        sys.exit(f"{CORPUS} not found: run build_corpus.py first")
    data = json.loads(CORPUS.read_text(encoding="utf-8"))
    return data["issues"], data.get("window")


def list_labels(issues):
    triaged = [i for i in issues if NOT_TRIAGED not in i["labels"]]
    counts = Counter(label for i in triaged for label in i["labels"])
    print(f"Labels on {len(triaged)} triaged issues in the corpus ( * = in AREA_LABELS):")
    for label, n in counts.most_common():
        print(f"  {'*' if label in AREA_LABELS else ' '} {n:5d}  {label}")


def report(rules, summary, near_misses, train_n, check_n, cutoff):
    print(f"\nLearned from {train_n} triaged issues created before {cutoff[:10]}; "
          f"checked on {check_n} created on or after it.\n")
    for label in AREA_LABELS:
        s = summary[label]
        recall = "n/a" if s["recall"] is None else f"{s['recall']:.0%}"
        print(f"{label}: found {s['found_by_rules']} of {s['check_issues']} later issues "
              f"with this label ({recall})")
        own = [r for r in rules if r["label"] == label]
        for r in own:
            t, c = r["train"], r["check"]
            later = "no later matches" if not c["matches"] else \
                f"later {c['correct']}/{c['matches']} = {c['precision']:.2f}"
            print(f"    {r['kind']:7s} {r['match']:<34s} earlier {t['hits']}/{t['support']}"
                  f" = {t['precision']}   {later}{'   (manual)' if r['source'] == 'manual' else ''}")
        if not own:
            print("    no rule passed the thresholds; closest candidates:")
            for r in sorted(near_misses[label], key=lambda r: -r["train"]["precision"])[:3]:
                t = r["train"]
                print(f"      {r['kind']:7s} {r['match']:<32s} earlier {t['hits']}/{t['support']}"
                      f" = {t['precision']}")


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--list-labels", action="store_true",
                        help="print label counts in the corpus and stop")
    args = parser.parse_args()

    issues, window = load_corpus()
    if args.list_labels:
        list_labels(issues)
        return

    if not TEST_CASE_ISSUES:
        sys.exit("Fill in TEST_CASE_ISSUES (the upstream numbers of your test cases) first")
    if not (PANDAS / "pandas").is_dir():
        sys.exit(f"No pandas clone found at {PANDAS.resolve()}")
    unknown = sorted(({*AREA_LABELS} | {r["label"] for r in MANUAL_RULES}) - real_labels())
    if unknown:
        sys.exit(f"Not real pandas labels (check spelling): {unknown}")

    by_number = {i["number"]: i for i in issues}
    missing = sorted(TEST_CASE_ISSUES - by_number.keys())
    if missing:
        print(f"Warning: test cases not in the corpus (move START earlier?): {missing}")
    if len(missing) == len(TEST_CASE_ISSUES):
        sys.exit("None of the test cases are in the corpus")
    if issues and "paths" not in issues[0]:
        print("Note: corpus has no 'paths' field; rerun the new build_corpus.py so traceback "
              "paths come from full issue bodies, not only the excerpt")
    cutoff = min(by_number[n]["created_at"] for n in TEST_CASE_ISSUES if n in by_number)

    pool = [i for i in issues if i["number"] not in TEST_CASE_ISSUES
            and NOT_TRIAGED not in i["labels"]]
    train = [i for i in pool if i["created_at"] < cutoff]
    later = [i for i in pool if i["created_at"] >= cutoff]
    if len(train) < 300:
        print(f"Warning: only {len(train)} training issues; move build_corpus START earlier")

    commit = run("git", "-C", str(PANDAS), "rev-parse", "HEAD").strip()
    print(f"Reading pandas {commit[:10]} at {PANDAS.resolve()} ...")
    vocabulary = pandas_vocabulary(PANDAS)
    print(f"{len(vocabulary)} pandas names in the vocabulary")

    rules, near_misses = learn(train, vocabulary, PANDAS)
    summary = check(rules, later, vocabulary)
    report(rules, summary, near_misses, len(train), len(later), cutoff)

    OUT.parent.mkdir(exist_ok=True)
    OUT.write_text(json.dumps({
        "pandas_commit": commit,
        "corpus_window": window,
        "cutoff": cutoff,
        "test_cases_left_out": sorted(TEST_CASE_ISSUES),
        "method": {
            "learned_from": f"{len(train)} triaged corpus issues created before the cutoff",
            "checked_on": f"{len(later)} triaged corpus issues created on or after the cutoff",
            "min_hits_keyword": MIN_HITS_KEYWORD, "min_hits_path": MIN_HITS_PATH,
            "min_precision": MIN_PRECISION, "max_rules_per_label": MAX_RULES_PER_LABEL,
            "ignored_keywords": sorted(IGNORE_KEYWORDS),
        },
        "matching": MATCHING,
        "vocabulary": sorted({r["match"] for r in rules if r["kind"] == "keyword"}),
        "labels": summary,
        "rules": rules,
    }, indent=1) + "\n", encoding="utf-8")
    print(f"\nwrote {OUT}: {len(rules)} rules for {len(AREA_LABELS)} labels")


if __name__ == "__main__":
    main()