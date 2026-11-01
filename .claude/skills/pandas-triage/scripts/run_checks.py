"""The checks job: deterministic evidence for the triage agent, and the scope gate.

In the workflow it reads the issue from environment variables (never from the command line,
so issue text cannot inject shell commands) and appends two lines to $GITHUB_OUTPUT:

    report=<one-line JSON>        evidence passed to the agent's prompt
    run_agent=true|false          false: the agent job is skipped (no AI credits used)

Environment: ISSUE_NUMBER, ISSUE_TITLE, ISSUE_BODY, ISSUE_CREATED, AUTHOR_ASSOC.

The agent is skipped when the issue used a form other than the bug form (not in scoped) or was
opened by a maintainer (OWNER, MEMBER or COLLABORATOR), as pandas does for Needs Triage.

Sandbox replay: if the title is listed in evals/as_of.json, the checks use that original
creation date instead of today's, so candidates and the version check see only what existed
then. Any other issue uses its own creation date (the live behaviour).

Offline use (tests, trying a case by hand):
    python run_checks.py --title-file evals/golden/05_x/title.txt \
        --body-file evals/golden/05_x/input.md --pretty
"""
import argparse
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

# Let Python find the other scripts in this folder, whatever folder the workflow runs from.
# The imports below must come after this line.
sys.path.insert(0, str(Path(__file__).resolve().parent))

from area_hints import area_hints                    # suggested area labels
from check_example import check_example              # static checks of the example
from find_candidates import find_candidates          # possible duplicates
from report_gaps import find_gaps, form_type, scope  # which form, scope, unfilled boxes
from validate_labels import ALLOWED                  # the labels the agent may add
from version_gap import version_gap                  # reported vs latest pandas version

# scripts/ -> pandas-triage/ -> skills/ -> .claude/ -> repository root
ROOT = Path(__file__).resolve().parents[4]
AS_OF = ROOT / "evals" / "as_of.json"
LABELS = ROOT / "data" / "labels.json"
# GitHub's author_association values for people with rights in the repo (as pandas checks)
MAINTAINERS = {"OWNER", "MEMBER", "COLLABORATOR"}
# pandas gives Usage Question no description; this one follows the maintainer guide
FALLBACK_MEANINGS = {"Usage Question": "How-to question, not a bug; pandas prefers these on "
                                       "StackOverflow"}


def normalise(title):
    """Trim the ends and collapse runs of spaces, tabs or newlines into one space, so a
    title matches its entry in as_of.json despite small whitespace differences
    (e.g. the bug form pre-fills 'BUG: ' with a trailing space; case 05's title is 'BUG:')."""
    return " ".join((title or "").split())


def as_of_date(title, created):
    """(date the checks should use, whether it came from evals/as_of.json).
    A replayed golden case gets its ORIGINAL creation date, so the duplicate search and
    the version check see only what existed then. Any other issue keeps its own date."""
    if AS_OF.exists():
        cases = json.loads(AS_OF.read_text(encoding="utf-8")).get("cases", {})
        listed = {normalise(t): v["as_of"] for t, v in cases.items()}
        if normalise(title) in listed:
            return listed[normalise(title)], True
    return created, False


def glossary():
    """Meaning of every label the agent may add, from pandas' own label descriptions.
    The agent cannot read data/ (not checked out in its job), so the meanings travel
    in the report."""
    described = {label["name"]: label["description"]
                 for label in json.loads(LABELS.read_text(encoding="utf-8"))}
    return {name: described.get(name) or FALLBACK_MEANINGS.get(name, "") for name in ALLOWED}


def build_report(number, title, body, created, assoc):
    """(report dict, run_agent bool)."""
    when, _replayed = as_of_date(title, created)

    # 1. The scope gate: cheap checks that decide whether the agent runs at all.
    report = {
        "issue": number,
        "form": form_type(body),
        "scope": scope(body),
        "author_is_maintainer": assoc in MAINTAINERS,
    }
    if report["scope"] == "out":
        report["skip_reason"] = f"filed with the {report['form']} form: not a bug report"
    elif report["author_is_maintainer"]:
        report["skip_reason"] = "opened by a maintainer"
    else:
        report["skip_reason"] = None
    run_agent = report["skip_reason"] is None

    # 2. The evidence, only when the agent will run (out-of-scope issues stop above).
    if run_agent:
        report.update({
            "gaps": find_gaps(body),
            "example": check_example(body),
            "version": version_gap(body, when),
            "candidates": find_candidates(title, body, when),
            "area_hints": area_hints(title, body),
            "allowed_labels": glossary(),
        })
    return report, run_agent


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--title-file")
    parser.add_argument("--body-file")
    parser.add_argument("--created", help="ISO date for offline runs (default: now)")
    parser.add_argument("--assoc", default="NONE")
    parser.add_argument("--pretty", action="store_true", help="indented JSON, for reading")
    args = parser.parse_args()

    # Where the issue comes from: files (offline tests) or environment variables (workflow).
    # In the workflow the issue text arrives through `env:`, never pasted into the shell
    # command, so a title like '"; rm -rf ~; echo "' stays plain text (no script injection).
    if args.body_file:                                  # offline
        number = 0
        title = Path(args.title_file).read_text(encoding="utf-8").strip() if args.title_file else ""
        body = Path(args.body_file).read_text(encoding="utf-8")
        created = args.created or datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        assoc = args.assoc
    else:                                               # in the workflow
        number = int(os.environ.get("ISSUE_NUMBER") or 0)
        title = os.environ.get("ISSUE_TITLE", "")
        body = os.environ.get("ISSUE_BODY", "")
        created = os.environ.get("ISSUE_CREATED") or datetime.now(timezone.utc).isoformat()
        assoc = os.environ.get("AUTHOR_ASSOC", "NONE")

    # Windows line endings from the browser -> \n, so the regexes behave the same everywhere
    report, run_agent = build_report(number, title, body.replace("\r\n", "\n"), created, assoc)
    if args.pretty:
        print(json.dumps(report, indent=1, ensure_ascii=False))
        print(f"run_agent={'true' if run_agent else 'false'}")
        return
    # one line each: $GITHUB_OUTPUT takes name=value lines, so the JSON must not contain
    # real newlines (json.dumps writes them as \n inside strings)
    print("report=" + json.dumps(report, ensure_ascii=False, separators=(",", ":")))
    print(f"run_agent={'true' if run_agent else 'false'}")


if __name__ == "__main__":
    main()
