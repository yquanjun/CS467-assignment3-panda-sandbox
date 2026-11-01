#!/usr/bin/env python3
"""Measure how many pandas bug reports leave form sections unfilled, and what happened to them.

Reads data/issues_corpus.json (built by build_corpus.py with the report_gaps field).
Read-only, no network. Run from your sandbox repo root:

    python tools/snapshots/measure_report_gaps.py
    python tools/snapshots/measure_report_gaps.py --since 2025-12-01 --until 2026-10-15 --list 30
    python tools/snapshots/measure_report_gaps.py --gap example_not_code   # one kind of gap

Use the numbers to show the need for the agent; use the list to pick golden cases
(open each link and check what the maintainer did).
"""
import argparse
import json
from collections import Counter
from pathlib import Path

CORPUS = Path("data/issues_corpus.json")
URL = "https://github.com/pandas-dev/pandas/issues/{}"
GAP_NAMES = {
    "versions_placeholder": "show_versions() placeholder line left in",
    "no_show_versions": "Installed Versions filled, but not with show_versions() output",
    "example_empty": "Reproducible Example empty or filler",
    "example_not_code": "Reproducible Example has no code",
    "description_empty": "Issue Description empty or filler",
    "expected_empty": "Expected Behavior empty or filler",
}


def pct(part, whole):
    return f"{part / whole:.0%}" if whole else "n/a"


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--since", default="2025-12-01", help="created on or after (YYYY-MM-DD)")
    parser.add_argument("--until", default="2026-10-15", help="created on or before (YYYY-MM-DD)")
    parser.add_argument("--list", type=int, default=20, help="examples to list (0 = none)")
    parser.add_argument("--gap", choices=GAP_NAMES,
                        help="list only reports with this gap, e.g. example_not_code")
    args = parser.parse_args()

    issues = json.loads(CORPUS.read_text(encoding="utf-8"))["issues"]
    if issues and "report_gaps" not in issues[0]:
        raise SystemExit("Corpus has no report_gaps field: rerun build_corpus.py first")

    window = [i for i in issues if args.since <= i["created_at"][:10] <= args.until]
    forms = [i for i in window if i["report_gaps"] is not None]   # bug/performance form reports
    gapped = [i for i in forms if i["report_gaps"]]

    print(f"Issues created {args.since} to {args.until}: {len(window)}")
    print(f"  written with the bug or performance form: {len(forms)}")
    print(f"  with at least one gap: {len(gapped)} ({pct(len(gapped), len(forms))} of form reports)\n")

    print("Gaps (an issue can have several):")
    counts = Counter(g for i in gapped for g in i["report_gaps"])
    for gap, label in GAP_NAMES.items():
        print(f"  {counts[gap]:5d}  {pct(counts[gap], len(forms)):>4}  {label}")

    def has(issue, label):
        return label in issue["labels"]

    def outcome(name, test):
        n = sum(test(i) for i in gapped)
        print(f"  {n:5d}  {pct(n, len(gapped)):>4}  {name}")

    print("\nWhat the reports with gaps look like now (labels as of the corpus build):")
    outcome("labelled Needs Info", lambda i: has(i, "Needs Info"))
    outcome("labelled Closing Candidate", lambda i: has(i, "Closing Candidate"))
    outcome("closed as not planned", lambda i: (i.get("state_reason") or "").upper() == "NOT_PLANNED")
    outcome("closed as completed", lambda i: (i.get("state_reason") or "").upper() == "COMPLETED")
    outcome("still labelled Needs Triage", lambda i: has(i, "Needs Triage"))
    print("\nCaveats: labels are current, not historical (find_label_history.py covers removed "
          "labels);\nreports later edited to fill a gap are not counted, so these are lower bounds;"
          "\na gap does not always mean a maintainer needed the information.")

    if args.list:
        rows = sorted((i for i in gapped if not has(i, "Needs Info")
                       and (not args.gap or args.gap in i["report_gaps"])),
                      key=lambda i: i["created_at"], reverse=True)
        which = f"gap {args.gap}" if args.gap else "gaps"
        print(f"\n=== Reports with {which} but no Needs Info label: {len(rows)}, "
              f"showing {min(len(rows), args.list)} ===")
        for i in rows[:args.list]:
            state = i["state"].lower() + (f" ({i['state_reason'].lower()})" if i.get("state_reason") else "")
            print(f"{i['created_at'][:10]}  #{i['number']}  {i['title'][:70]}")
            print(f"    gaps: {', '.join(i['report_gaps'])} | {state} | labels: {', '.join(i['labels']) or '-'}")
            print(f"    {URL.format(i['number'])}")


if __name__ == "__main__":
    main()