#!/usr/bin/env python3
"""Build data/issues_corpus.json: to retrieve earlier pandas issues, which will be used to look for duplicates.
and (by build_structure.py) to learn which signals go with which area label.
Run from the root of your sandbox repo (logged in with `gh auth login`):

    python tools/snapshots/build_corpus.py

Set START and END below first. Your find_candidates.py must still filter
this file to issues created BEFORE each test case's original date.
"""
import json
import re
import subprocess
import time
from datetime import date, timedelta
from pathlib import Path

from report_gaps import find_gaps   # report_gaps.py sits next to this script

REPO = "pandas-dev/pandas"
START = date(2025, 5, 1)     # a few months before your earliest golden case
END = date(2026, 10, 31)     # your latest golden case's date (or today)
BODY_CHARS = 800             # keep only the start of each issue body
FIELDS = "number,title,state,stateReason,labels,createdAt,closedAt,body"
OUT = Path("data/issues_corpus.json")

# @username not preceded by a letter, digit or backtick (so e-mail addresses are left alone)
MENTION = re.compile(r"(?<![\w`])@([A-Za-z0-9][A-Za-z0-9-]{0,38})")

# Issue-form sections that are the same in every issue (checkboxes, show_versions output).
# They are cut before the excerpt is taken, so the excerpt holds the example and description.
BOILERPLATE = re.compile(
    r"^###[ \t]*(?:Pandas version checks|Installed Versions|Feature Type|Installation check)"
    r"[ \t\r]*$.*?(?=^###[ \t]|\Z)",
    re.S | re.M | re.I,
)
HTML_COMMENT = re.compile(r"<!--.*?-->", re.S)

# pandas file paths as they appear in tracebacks (/ or \ separators). build_structure.py
# uses the same pattern, so keep the two in step if you change it.
PANDAS_PATH = re.compile(r"pandas[\\/]+(?:[\w.-]+[\\/]+)*[\w.-]+\.(?:py|pyx|pyi)")


def strip_mentions(text):
    """Turn '@someone' into 'someone' outside ``` code blocks (decorators stay intact)."""
    parts = text.split("```")
    for i in range(0, len(parts), 2):        # even-numbered parts are outside code blocks
        parts[i] = MENTION.sub(r"\1", parts[i])
    return "```".join(parts)


def clean_body(body):
    """Drop HTML comments and the boilerplate form sections."""
    return BOILERPLATE.sub("", HTML_COMMENT.sub("", body)).strip()


def traceback_paths(body):
    """pandas file paths mentioned anywhere in the FULL body, e.g. 'pandas/core/groupby/ops.py'."""
    found = set()
    for raw in PANDAS_PATH.findall(body):
        path = re.sub(r"[\\/]+", "/", raw)
        found.add(path[path.rfind("pandas/"):])   # drop site-packages/..., URLs, etc.
    return sorted(found)[:20]


def month_ranges(start, end):
    """Yield (first_day, last_day) for each calendar month between start and end."""
    current = start.replace(day=1)
    while current <= end:
        next_month = (current.replace(day=28) + timedelta(days=4)).replace(day=1)
        yield max(current, start), min(next_month - timedelta(days=1), end)
        current = next_month


def fetch(first, last):
    cmd = [
        "gh", "issue", "list", "-R", REPO, "--state", "all", "--limit", "1000",
        "--search", f"created:{first}..{last}", "--json", FIELDS,
    ]
    # gh prints UTF-8; say so explicitly, or Windows decodes it as cp1252 and fails
    result = subprocess.run(cmd, check=True, capture_output=True, text=True, encoding="utf-8")
    return json.loads(result.stdout)


def clean(issue):
    closed = issue.get("closedAt")
    if not closed or closed.startswith("0001"):   # some tools use year 1 for "no date"
        closed = None
    body = issue.get("body") or ""
    return {
        "number": issue["number"],
        "title": issue["title"],
        "state": issue["state"],
        "state_reason": issue.get("stateReason"),
        "labels": sorted(label["name"] for label in issue.get("labels", [])),
        "created_at": issue["createdAt"],
        "closed_at": closed,
        "body_excerpt": strip_mentions(clean_body(body)[:BODY_CHARS]),
        "paths": traceback_paths(body),
        # gaps in the bug/performance form, from the FULL body (None = not that form).
        # Current text: a report later edited to fill a gap no longer shows that gap.
        "report_gaps": find_gaps(body),
    }


def main():
    rows = []
    for first, last in month_ranges(START, END):
        batch = fetch(first, last)
        print(f"{first}..{last}: {len(batch)} issues")
        if len(batch) >= 1000:
            raise SystemExit(f"{first}..{last} hit GitHub's 1000-result limit: "
                             "split that month into two halves and rerun")
        rows.extend(clean(issue) for issue in batch)
        time.sleep(3)                               # stay well under the search rate limit
    rows.sort(key=lambda r: r["number"])
    OUT.parent.mkdir(exist_ok=True)
    OUT.write_text(json.dumps(
        {"repo": REPO, "window": [str(START), str(END)], "issues": rows}, indent=1) + "\n",
        encoding="utf-8")
    print(f"wrote {len(rows)} issues to {OUT}")


if __name__ == "__main__":
    main()