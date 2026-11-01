"""Find earlier pandas bug reports that may describe the same problem.

Keyword search over data/issues_corpus.json, using only what existed when the new issue
was opened:
  - only issues created strictly before `as_of` (so never the issue itself);
  - "closed" is reported only if the issue was closed before `as_of`;
  - no labels, states or close reasons: the corpus stores them as they are today.

Score: shared words and pandas file paths, each weighted by how rare it is in the corpus
(inverse document frequency); words in the candidate's title count double. The agent
decides whether a candidate is the same problem; this script only shortlists.

    from find_candidates import find_candidates
    find_candidates(title, body, as_of)  ->  [{"issue": "pandas issue 61707", "number": 61707,
        "title": "...", "created": "2025-06-25", "closed_before": False,
        "score": 41.2, "shared": ["describe", "pint", ...], "excerpt": "..."}]

    python find_candidates.py 2026-10-06T22:52:00Z "issue title" < issue_body.md
"""
import json
import math
import re
import sys
from collections import Counter
from pathlib import Path

from corpus_text import PANDAS_PATH, clean_body, strip_mentions, traceback_paths

# scripts/ -> pandas-triage/ -> skills/ -> .claude/ -> repository root
ROOT = Path(__file__).resolve().parents[4]
CORPUS = ROOT / "data" / "issues_corpus.json"

MAX_CANDIDATES = 5        # keep the report short: fewer tokens for the agent to read
MIN_SCORE = 20.0          # below this a "candidate" is mostly noise (checked on the golden cases)
EXCERPT_CHARS = 240       # how much of each candidate's text the agent sees

# A "word": starts with a letter or _, at least 3 characters (so 'df', 'pd', 'a' are ignored)
WORD = re.compile(r"[A-Za-z_][A-Za-z0-9_]{2,}")

# Words that appear in almost every report and say nothing about the problem: English filler,
# the bug form's own headings, generic pandas words, and the noise in tracebacks
# (folder names) and pasted images (<img width= ...>). IDF would already give them low
# weight; removing them also keeps the "shared" list readable.
STOPWORDS = set("""
the and for with that this from not are but was were have has had when then than into
out can cannot does doesn did should would could will also only just more most some any
all one two its it's which what where who how why there their them they you your our
use used using get gets got set sets make makes new old same other else true false none
import pandas pd numpy np print df series dataframe data value values result results code
bug issue example expected behavior behaviour description reproducible output error
python version versions installed latest main branch confirmed checked reported exists
following above below like see shows show work works working
home site packages lib line file module traceback recent call last users appdata local
envs anaconda3 miniconda3 venv python3 __init__ img width height alt src https http github com
user attachments assets
""".split())


def words(text):
    """Lower-case words of 3+ characters, without stop words and without file paths
    (paths are compared separately, as whole paths)."""
    text = PANDAS_PATH.sub(" ", text)
    return {w.lower() for w in WORD.findall(text)} - STOPWORDS


def load_corpus():
    return json.loads(CORPUS.read_text(encoding="utf-8"))["issues"]


def find_candidates(title, body, as_of, corpus=None, limit=MAX_CANDIDATES):
    corpus = load_corpus() if corpus is None else corpus

    # 1. Only issues that existed when the new issue was opened. Strictly earlier, so the
    #    original of a replayed case (created exactly at as_of) is never its own candidate.
    pool = [i for i in corpus if i["created_at"] < as_of]
    if not pool:
        return []

    # 2. The words and paths of each earlier issue. The corpus keeps the title, the first
    #    800 cleaned characters of the body, and the pandas paths found in the full body.
    docs = []
    for issue in pool:
        title_words = words(issue["title"])
        all_words = title_words | words(issue.get("body_excerpt") or "")
        paths = set(issue.get("paths") or [])
        docs.append((issue, title_words, all_words, paths))

    # 3. Document frequency: in how many earlier issues each word or path appears.
    frequency = Counter()
    for _, _, all_words, paths in docs:
        frequency.update(all_words)
        frequency.update(paths)
    n = len(docs)

    def idf(term):
        """Weight of a term: high when few earlier issues contain it, 0 when all do.
        With about 1,500 issues: in 1 issue -> 6.6, in 150 -> 2.3, in all -> 0.
        The +1s avoid dividing by zero and keep the weight at 0 or above."""
        return math.log((n + 1) / (frequency[term] + 1))

    # 4. The new issue's words (title + cleaned body, without the version checks and
    #    show_versions boxes) and the pandas paths in its tracebacks.
    query_words = words(title) | words(clean_body(body or ""))
    query_paths = set(traceback_paths(body or ""))

    # 5. Score every earlier issue by what it shares with the new one.
    scored = []
    for issue, title_words, all_words, paths in docs:
        shared = query_words & all_words
        shared_paths = query_paths & paths
        if not shared and not shared_paths:
            continue
        # rare shared words count most; a shared word in the candidate's TITLE counts double
        score = sum(idf(w) * (2 if w in title_words else 1) for w in shared)
        # a shared pandas file path (same code in both tracebacks) is strong evidence
        score += sum(1.5 * idf(p) for p in shared_paths)
        if score >= MIN_SCORE:
            # the 6 rarest shared words, plus shared paths: shown to the agent as "why".
            # Ties sorted alphabetically: sets have no fixed order, and the report should be
            # identical every time the same issue is checked.
            top = sorted(shared, key=lambda w: (-idf(w), w))[:6] + sorted(shared_paths)
            scored.append((score, issue, top))

    # 6. Best first; ties broken by issue number so the output is always the same.
    scored.sort(key=lambda s: (-s[0], s[1]["number"]))

    # 7. What the agent sees. No labels, state or close reason (those are today's values);
    #    "closed_before" only if it was closed before the new issue was opened.
    results = []
    for score, issue, top in scored[:limit]:
        closed = issue.get("closed_at")
        text = re.sub(r"\s+", " ", strip_mentions(issue.get("body_excerpt") or "")).strip()
        results.append({
            "issue": f"pandas issue {issue['number']}",   # plain text: '#N' would link here
            "number": issue["number"],
            "title": issue["title"],
            "created": issue["created_at"][:10],
            "closed_before": bool(closed and closed < as_of),
            "score": round(score, 1),
            "shared": top,
            "excerpt": text[:EXCERPT_CHARS],
        })
    return results


if __name__ == "__main__":
    print(json.dumps(find_candidates(sys.argv[2], sys.stdin.read(), sys.argv[1]), indent=1))
