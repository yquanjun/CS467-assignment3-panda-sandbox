#!/usr/bin/env python3
"""Measure how long pandas bug reports wait for a first maintainer action, and for triage.

For bug reports (form 'bug' in data/issues_corpus.json) created in the window, it reads
each issue's timeline through the GitHub GraphQL API (read-only), finds the first action
by a maintainer and when Needs Triage was removed, writes one row per issue to
metrics/first_response.csv, and prints a summary for metrics/results.md.

Run from your sandbox repo root, logged in with `gh auth login`, after build_corpus.py:

    python tools/snapshots/measure_first_response.py
    python tools/snapshots/measure_first_response.py --since 2026-08-01 --until 2026-10-31

Definitions (state them in metrics/README.md):
  maintainer action  a comment whose author association is OWNER, MEMBER or COLLABORATOR,
                     or a label change, close, assignment, milestone or title change made by
                     someone other than the reporter and not a bot. Only people with triage
                     rights can do those to someone else's issue. The bug form's own labels
                     show up as label events by the reporter at creation, so they don't count.
  outsider report    reporter's association is not OWNER, MEMBER or COLLABORATOR
                     (maintainers' own issues skip triage, so they are left out).
Cost: one query per 50 issues (about 1 point each from 5,000 points per hour). No Copilot credits.
"""
import argparse
import csv
import json
import math
import statistics
import subprocess
import time
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

REPO = "pandas-dev/pandas"
CORPUS = Path("data/issues_corpus.json")
OUT = Path("metrics/first_response.csv")
MAINTAINER_ASSOC = {"OWNER", "MEMBER", "COLLABORATOR"}
KNOWN_BOTS = {"github-actions", "dependabot", "pre-commit-ci", "meeseeksmachine"}
NEEDS_TRIAGE = "Needs Triage"

QUERY = """
query($q: String!, $cursor: String) {
  search(type: ISSUE, query: $q, first: 50, after: $cursor) {
    issueCount
    pageInfo { hasNextPage endCursor }
    nodes {
      ... on Issue {
        number url createdAt authorAssociation
        author { __typename login }
        timelineItems(first: 100, itemTypes: [ISSUE_COMMENT, LABELED_EVENT, UNLABELED_EVENT,
                      CLOSED_EVENT, ASSIGNED_EVENT, MILESTONED_EVENT, RENAMED_TITLE_EVENT]) {
          nodes {
            __typename
            ... on IssueComment      { createdAt authorAssociation author { __typename login } }
            ... on LabeledEvent      { createdAt actor { __typename login } label { name } }
            ... on UnlabeledEvent    { createdAt actor { __typename login } label { name } }
            ... on ClosedEvent       { createdAt actor { __typename login } }
            ... on AssignedEvent     { createdAt actor { __typename login } }
            ... on MilestonedEvent   { createdAt actor { __typename login } }
            ... on RenamedTitleEvent { createdAt actor { __typename login } }
          }
        }
      }
    }
  }
}
"""
EVENT_NAMES = {
    "IssueComment": "comment", "LabeledEvent": "label added", "UnlabeledEvent": "label removed",
    "ClosedEvent": "closed", "AssignedEvent": "assigned", "MilestonedEvent": "milestone set",
    "RenamedTitleEvent": "title changed",
}


def run_query(search, cursor):
    cmd = ["gh", "api", "graphql", "-f", f"query={QUERY}", "-f", f"q={search}"]
    if cursor:
        cmd += ["-f", f"cursor={cursor}"]
    # gh prints UTF-8; say so explicitly, or Windows decodes it as cp1252
    out = subprocess.run(cmd, check=True, capture_output=True, text=True, encoding="utf-8").stdout
    return json.loads(out)["data"]["search"]


def month_ranges(start, end):
    """(first_day, last_day) per calendar month; search returns at most 1,000 results."""
    current = start.replace(day=1)
    while current <= end:
        next_month = (current.replace(day=28) + timedelta(days=4)).replace(day=1)
        yield max(current, start), min(next_month - timedelta(days=1), end)
        current = next_month


def when(text):
    return datetime.fromisoformat(text.replace("Z", "+00:00"))


def is_bot(person):
    if not person:                       # deleted account ("ghost")
        return False
    login = person.get("login") or ""
    return (person.get("__typename") == "Bot" or login.endswith("[bot]")
            or login.removesuffix("[bot]") in KNOWN_BOTS)


def first_maintainer_action(issue):
    """(time, kind, login) of the earliest maintainer action, or None."""
    reporter = (issue.get("author") or {}).get("login")
    for item in issue["timelineItems"]["nodes"]:          # oldest first
        if not item:
            continue
        kind = item["__typename"]
        if kind == "IssueComment":
            person = item.get("author")
            ok = item.get("authorAssociation") in MAINTAINER_ASSOC
        else:
            person = item.get("actor")
            ok = True
        login = (person or {}).get("login")
        if ok and person and login != reporter and not is_bot(person):
            return when(item["createdAt"]), EVENT_NAMES[kind], login
    return None


def triage_removed(issue):
    """Time Needs Triage was first removed by a person (not a bot), or None."""
    for item in issue["timelineItems"]["nodes"]:
        if (item and item["__typename"] == "UnlabeledEvent"
                and (item.get("label") or {}).get("name") == NEEDS_TRIAGE
                and not is_bot(item.get("actor"))):
            return when(item["createdAt"])
    return None


def percentile(values, share):
    """Nearest-rank percentile of a non-empty list: the value at rank ceil(share * n)."""
    ordered = sorted(values)
    return ordered[max(1, math.ceil(share * len(ordered))) - 1]


def hours(delta):
    return round(delta.total_seconds() / 3600, 1)


def fmt_hours(h):
    return f"{h:.1f} h" if h < 48 else f"{h / 24:.1f} days"


def pct(part, whole):
    return f"{part / whole:.0%}" if whole else "n/a"


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--since", default="2026-08-01", help="bug reports created on or after")
    parser.add_argument("--until", default="2026-10-31", help="bug reports created on or before")
    parser.add_argument("--include-members", action="store_true",
                        help="also count issues opened by maintainers (left out by default)")
    args = parser.parse_args()

    corpus = json.loads(CORPUS.read_text(encoding="utf-8"))["issues"]
    if corpus and "form" not in corpus[0]:
        raise SystemExit("Corpus has no 'form' field: rerun build_corpus.py first")
    bug_reports = {i["number"]: i for i in corpus if i["form"] == "bug"}

    rows, skipped_members = [], 0
    now = datetime.now(timezone.utc)
    for first, last in month_ranges(date.fromisoformat(args.since), date.fromisoformat(args.until)):
        search = f"repo:{REPO} is:issue created:{first}..{last}"
        cursor, seen = None, 0
        while True:
            page = run_query(search, cursor)
            if page["issueCount"] > 1000:
                raise SystemExit(f"{first}..{last} has over 1,000 issues; use a shorter range")
            for issue in page["nodes"]:
                if not issue or issue["number"] not in bug_reports:
                    continue                   # not an issue, or not a bug-form report
                if issue["authorAssociation"] in MAINTAINER_ASSOC and not args.include_members:
                    skipped_members += 1
                    continue
                seen += 1
                created = when(issue["createdAt"])
                action = first_maintainer_action(issue)
                removed = triage_removed(issue)
                info = bug_reports[issue["number"]]
                rows.append({
                    "number": issue["number"],
                    "url": issue["url"],
                    "created_at": issue["createdAt"],
                    "author_association": issue["authorAssociation"],
                    "report_gaps": ";".join(info.get("report_gaps") or []),
                    "first_action_at": action[0].isoformat() if action else "",
                    "first_action_type": action[1] if action else "",
                    "first_action_by": action[2] if action else "",
                    "hours_to_first_action": hours(action[0] - created) if action else "",
                    "needs_triage_removed_at": removed.isoformat() if removed else "",
                    "hours_to_triage": hours(removed - created) if removed else "",
                    "age_days_at_collection": round((now - created).total_seconds() / 86400, 1),
                    "labels_now": ";".join(info.get("labels") or []),
                })
            if not page["pageInfo"]["hasNextPage"]:
                break
            cursor = page["pageInfo"]["endCursor"]
            time.sleep(1)                       # be gentle with the API
        print(f"{first}..{last}: {seen} outsider bug reports")

    OUT.parent.mkdir(exist_ok=True)
    with OUT.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0]) if rows else ["number"])
        writer.writeheader()
        writer.writerows(rows)

    # ---- summary for metrics/results.md ----
    n = len(rows)
    acted = [r["hours_to_first_action"] for r in rows if r["hours_to_first_action"] != ""]
    print(f"\nBug reports by outsiders, created {args.since} to {args.until}: {n}"
          f" (left out {skipped_members} opened by maintainers)")
    print(f"Collected {now:%Y-%m-%d %H:%M} UTC; wrote {OUT}")
    if not n:
        return
    print("\nTime to first maintainer action:")
    print(f"  with an action so far: {len(acted)} ({pct(len(acted), n)}); none yet: {n - len(acted)}")
    if acted:
        print(f"  median: {fmt_hours(statistics.median(acted))};"
              f" 90th percentile: {fmt_hours(percentile(acted, 0.9))}")
    for limit_days in (1, 7):
        old_enough = [r for r in rows if r["age_days_at_collection"] >= limit_days]
        within = sum(1 for r in old_enough if r["hours_to_first_action"] != ""
                     and r["hours_to_first_action"] <= limit_days * 24)
        print(f"  acted on within {limit_days} day(s): {within} of {len(old_enough)}"
              f" ({pct(within, len(old_enough))})")

    print("\nTriage (Needs Triage removed):")
    for limit_days in (7, 30):
        old_enough = [r for r in rows if r["age_days_at_collection"] >= limit_days]
        waiting = sum(1 for r in old_enough if r["hours_to_triage"] == ""
                      or r["hours_to_triage"] > limit_days * 24)
        print(f"  still untriaged after {limit_days} days: {waiting} of {len(old_enough)}"
              f" ({pct(waiting, len(old_enough))})")

    with_gaps = [r for r in rows if r["report_gaps"]]
    complete = [r for r in rows if not r["report_gaps"]]
    for name, group in (("with a template gap", with_gaps), ("complete", complete)):
        times = [r["hours_to_first_action"] for r in group if r["hours_to_first_action"] != ""]
        median = fmt_hours(statistics.median(times)) if times else "n/a"
        print(f"  reports {name}: {len(group)}, median wait {median}")
    print("\nOnly issues at least 1, 7 or 30 days old count towards those limits;"
          " 'none yet' is as of the collection time.")


if __name__ == "__main__":
    main()