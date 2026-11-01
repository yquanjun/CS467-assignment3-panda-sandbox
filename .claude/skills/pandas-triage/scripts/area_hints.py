"""Suggest area labels from the rules in data/structure.json.

The rules were learned (and checked) by tools/snapshots/build_structure.py on earlier triaged
bug reports. The three matching functions below are copied from that script, and the issue
is cleaned the way the corpus was, so a rule matches here exactly as it did when it was learned:
  - names come from the title and the cleaned first 800 characters of the body;
  - paths come from the whole body.

Each hint carries the rule that matched and how often that rule was right on the checking
set ('precision'), so the agent can weigh weak hints. Rules that were right less than half
the time there are not used at all (MIN_CHECK_PRECISION).

    from area_hints import area_hints
    area_hints(title, body)  ->  [{"label": "Strings", "because": ["keyword StringDtype"],
                                   "precision": 0.83}]

    python area_hints.py "issue title" < issue_body.md
"""
import json
import re
import sys
from pathlib import Path

from corpus_text import excerpt, traceback_paths

# scripts/ -> pandas-triage/ -> skills/ -> .claude/ -> repository root
ROOT = Path(__file__).resolve().parents[4]
STRUCTURE = ROOT / "data" / "structure.json"
# Rules right less often than this on the checking set are ignored (e.g. 'concat' -> Reshaping
# was right 23% of the time). Unmeasured rules (never fired) are kept.
MIN_CHECK_PRECISION = 0.5

IDENTIFIER_RE = r"[A-Za-z_][A-Za-z0-9_]*"
PATH_RE = r"pandas[\\/]+(?:[\w.-]+[\\/]+)*[\w.-]+\.(?:py|pyx|pyi)"   # same as build_structure.py


# ---------- copied from tools/snapshots/build_structure.py (keep in step) ----------

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

# -----------------------------------------------------------------------------------


def rule_precision(rule):
    """Precision on the checking set, or on the training set when the rule never fired there."""
    # 'check' = the issues after the cutoff (not used for learning), so it is the honest figure
    check = rule.get("check") or {}
    if check.get("matches"):
        return check["precision"]
    return (rule.get("train") or {}).get("precision")


def area_hints(title, body, structure=None):
    if structure is None:
        structure = json.loads(STRUCTURE.read_text(encoding="utf-8"))
    vocabulary = set(structure["vocabulary"])
    # The same signals the rules were learned from: names in the title + first 800 cleaned
    # characters (so a library listed in show_versions does not count), paths in the whole body.
    names = find_names(f"{title}\n{excerpt(body)}", vocabulary)
    paths = set(traceback_paths(body or ""))
    hints = {}                                   # label -> its hint (one hint per label)
    for rule in structure["rules"]:
        precision = rule_precision(rule)
        # skip only rules KNOWN to be weak; 'is not None' also avoids comparing None < 0.5
        if precision is not None and precision < MIN_CHECK_PRECISION:
            continue
        if rule_matches(rule, names, paths):
            # several rules can point to the same label: merge them into one hint that lists
            # every matching rule ("because") and keeps the best rule's precision
            hint = hints.setdefault(rule["label"], {"label": rule["label"], "because": [],
                                                    "precision": 0.0})
            hint["because"].append(f"{rule['kind']} {rule['match']}")
            hint["precision"] = max(hint["precision"], round(precision or 0.0, 2))
    # strongest hint first; ties in label order so the output is always the same
    return sorted(hints.values(), key=lambda h: (-h["precision"], h["label"]))


if __name__ == "__main__":
    print(json.dumps(area_hints(sys.argv[1], sys.stdin.read()), indent=1))
