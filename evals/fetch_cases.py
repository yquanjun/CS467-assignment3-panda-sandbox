#!/usr/bin/env python3
"""Fetch each golden case's ORIGINAL title and body from pandas and write the case files.

For every case below it writes, inside evals/golden/<folder>/:
  title.txt      original title (before any rename), to paste into the bug form
  input.md       original body (earliest revision), with @mentions and pandas links neutralised
  source.md      facts for the reviewer: dates, revision used, labels at opening, maintainer evidence
  revisions.md   every saved revision of the body, raw, so you can check the choice by hand
and writes evals/as_of.json (original title -> original creation date) for the checks job.

Read-only: it only runs GraphQL queries with your gh login. Existing input.md and title.txt
are kept unless you pass --force (so your manual fixes are not overwritten).
expected.yaml is never touched.

    python evals/fetch_cases.py
    python evals/fetch_cases.py --force
"""
import argparse
import json
import re
import subprocess
from pathlib import Path

CASES = {          # folder name -> upstream pandas issue number
    "01_complete_70991": 70991,
    "02_complete_67726": 67726,
    "03_optional_box_unticked_71275": 71275,
    "04_version_not_provided_64253": 64253,
    "05_example_cannot_run_63757": 63757,
    "06_environment_63269": 63269,
    "07_usage_question_63271": 63271,
    "08_feature_request_63277": 63277,
    "09_another_library_64298": 64298,
    "10_duplicate_70748": 70748,
    "11_out_of_scope_65834": 65834,
}
GOLDEN = Path("evals/golden")
AS_OF = Path("evals/as_of.json")
MAINTAINERS = {"OWNER", "MEMBER", "COLLABORATOR"}

QUERY = """
query($number: Int!) {
  repository(owner: "pandas-dev", name: "pandas") {
    issue(number: $number) {
      number title url createdAt authorAssociation state stateReason body
      author { login }
      labels(first: 30) { nodes { name } }
      userContentEdits(first: 100) { nodes { createdAt editedAt diff } }
      timelineItems(first: 100, itemTypes: [RENAMED_TITLE_EVENT, LABELED_EVENT, ISSUE_COMMENT, CLOSED_EVENT]) {
        nodes {
          __typename
          ... on RenamedTitleEvent { createdAt previousTitle currentTitle actor { login } }
          ... on LabeledEvent { createdAt label { name } actor { login } }
          ... on IssueComment { createdAt authorAssociation body author { login } }
          ... on ClosedEvent { createdAt stateReason actor { login } }
        }
      }
    }
  }
}
"""

FENCE = "```"
MENTION = re.compile(r"(?<![\w`])@([A-Za-z0-9][A-Za-z0-9-]{0,38})")
PANDAS_URL = re.compile(r"https?://github\.com/pandas-dev/pandas/(issues|pull)/(\d+)(?:#[\w-]+)?")
PANDAS_REF = re.compile(r"\bpandas-dev/pandas#(\d+)")
GH_REF = re.compile(r"\bGH ?#?(\d{3,6})\b")
BARE_REF = re.compile(r"(?<![\w&/#])#(\d{3,6})\b")


def run_query(number):
    cmd = ["gh", "api", "graphql", "-f", f"query={QUERY}", "-F", f"number={number}"]
    # gh prints UTF-8; say so explicitly, or Windows decodes it as cp1252
    out = subprocess.run(cmd, check=True, capture_output=True, text=True, encoding="utf-8").stdout
    return json.loads(out)["data"]["repository"]["issue"]


def neutralise(text):
    """Remove what would notify real people or link back to pandas when the text is re-filed:
    @mentions and references to pandas issues (outside ``` code blocks)."""
    text = PANDAS_URL.sub(lambda m: f"pandas {'issue' if m[1] == 'issues' else 'pull request'} {m[2]}", text)
    text = PANDAS_REF.sub(r"pandas issue \1", text)
    parts = text.split(FENCE)
    for i in range(0, len(parts), 2):          # even parts are outside code blocks
        parts[i] = MENTION.sub(r"\1", parts[i])
        parts[i] = GH_REF.sub(r"pandas issue \1", parts[i])
        parts[i] = BARE_REF.sub(r"pandas issue \1", parts[i])
    return FENCE.join(parts)


def original_title(issue):
    renames = sorted((n for n in issue["timelineItems"]["nodes"]
                      if n and n["__typename"] == "RenamedTitleEvent"), key=lambda n: n["createdAt"])
    return (renames[0]["previousTitle"] if renames else issue["title"]), renames


def original_body(issue):
    """The earliest saved revision, or the current body if it was never edited.
    GitHub keeps each revision's full text in the edit's 'diff' field; check revisions.md."""
    edits = [e for e in issue["userContentEdits"]["nodes"] if e and e.get("diff") is not None]
    if not edits:
        return issue["body"] or "", "never edited: current body used", edits
    edits.sort(key=lambda e: e.get("editedAt") or e["createdAt"])
    return edits[0]["diff"], f"edited {len(edits) - 1} time(s): earliest of {len(edits)} revisions used", edits


def source_md(folder, issue, title, renames, body_note):
    created = issue["createdAt"]
    nodes = [n for n in issue["timelineItems"]["nodes"] if n]
    reporter = (issue.get("author") or {}).get("login")
    at_opening = sorted({n["label"]["name"] for n in nodes if n["__typename"] == "LabeledEvent"
                         and (n.get("actor") or {}).get("login") == reporter
                         and n["createdAt"][:16] <= created[:16]})
    by_others = [f"{n['createdAt'][:10]} {n['label']['name']}" for n in nodes
                 if n["__typename"] == "LabeledEvent" and (n.get("actor") or {}).get("login") != reporter
                 and not ((n.get("actor") or {}).get("login") or "").startswith("github-actions")]
    comments = [n for n in nodes if n["__typename"] == "IssueComment"
                and n.get("authorAssociation") in MAINTAINERS]
    closed = [n for n in nodes if n["__typename"] == "ClosedEvent"]
    lines = [
        f"# {folder}",
        "",
        f"- Upstream: pandas issue {issue['number']} (plain text on purpose: no links in issues)",
        f"- Opened: {created}; reporter association: {issue['authorAssociation']}",
        f"- Original title: {title}",
        f"- Current title: {issue['title']}" + (" (renamed)" if renames else " (unchanged)"),
        f"- Body: {body_note}",
        f"- Labels at opening (form): {', '.join(at_opening) or 'none'}",
        f"- Labels added later by others: {'; '.join(by_others) or 'none'}",
        f"- Labels now: {', '.join(l['name'] for l in issue['labels']['nodes'])}",
        f"- State now: {issue['state']}" + (f" ({issue['stateReason']})" if issue.get("stateReason") else ""),
        "",
        "## Maintainer responses (evidence for expected.yaml)",
    ]
    for c in comments[:4]:
        text = neutralise((c.get("body") or "").strip()).replace("\r", "")
        lines += ["", f"**{c['createdAt'][:10]}, {c['authorAssociation'].lower()}:**", "",
                  "> " + text[:700].replace("\n", "\n> ")]
    if not comments:
        lines += ["", "No maintainer comments."]
    for c in closed:
        lines += ["", f"Closed {c['createdAt'][:10]} ({c.get('stateReason') or 'no reason'})."]
    return "\n".join(lines) + "\n"


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--force", action="store_true", help="overwrite existing input.md and title.txt")
    args = parser.parse_args()

    as_of = {"note": "Sandbox replay only: run_checks.py uses the original creation date for an issue "
                     "whose title is listed here, so checks see only what existed then.",
             "cases": {}}
    for folder, number in CASES.items():
        issue = run_query(number)
        title, renames = original_title(issue)
        body, note, edits = original_body(issue)
        out = GOLDEN / folder
        out.mkdir(parents=True, exist_ok=True)
        for name, content in (("title.txt", title + "\n"),
                              ("input.md", neutralise(body).replace("\r\n", "\n").rstrip() + "\n")):
            path = out / name
            if path.exists() and not args.force:
                print(f"  kept existing {path}")
            else:
                path.write_text(content, encoding="utf-8")
        (out / "source.md").write_text(source_md(folder, issue, title, renames, note), encoding="utf-8")
        revs = [f"# Revisions of pandas issue {number} body (raw, oldest first)\n"]
        for e in sorted(edits, key=lambda e: e.get("editedAt") or e["createdAt"]):
            revs += [f"\n## {e.get('editedAt') or e['createdAt']}\n", (e.get("diff") or "").replace("\r", "")]
        if not edits:
            revs.append("\nNever edited.\n")
        (out / "revisions.md").write_text("\n".join(revs) + "\n", encoding="utf-8")
        as_of["cases"][title] = {"as_of": issue["createdAt"], "case": folder}
        print(f"{folder}: '{title[:60]}' opened {issue['createdAt'][:10]}; {note}")
    AS_OF.write_text(json.dumps(as_of, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"\nwrote {AS_OF}. Check each input.md against the issue's 'edited' history before committing.")


if __name__ == "__main__":
    main()
