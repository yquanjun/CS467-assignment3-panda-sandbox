"""Check labels before proposing them. The agent runs this; it needs no data files.

    python3 .claude/skills/pandas-triage/scripts/validate_labels.py "Usage Question" "IO CSV"

Prints OK (exit 0) or the problems (exit 1). The same allowlist, blocked list and limit are
enforced by the workflow's safe outputs, so this is a check, not the control.
Keep ALLOWED and BLOCKED in step with .github/workflows/pandas-triage.md (tests compare them).
"""
import sys

AREA_LABELS = ["Strings", "Arrow", "IO XML", "Reshaping", "Visualization", "IO CSV",
               "expressions", "IO Parquet"]
TRIAGE_LABELS = ["Usage Question", "Needs Discussion", "Closing Candidate"]
ALLOWED = AREA_LABELS + TRIAGE_LABELS
BLOCKED = ["Needs Triage", "Needs Info", "Duplicate Report", "Regression"]
MAX_LABELS = 2                 # safe outputs: add-labels max-labels: 2


def validate(labels):
    """List of problems; empty when the labels can be proposed."""
    problems = []
    if len(labels) > MAX_LABELS:
        problems.append(f"{len(labels)} labels given; at most {MAX_LABELS} in one call")
    if len(set(labels)) != len(labels):
        problems.append("a label is repeated")
    for label in labels:
        if label in BLOCKED:
            problems.append(f"'{label}' is blocked: only maintainers add it")
        elif label not in ALLOWED:
            # suggest the right spelling when only the capitals differ ('io csv' -> 'IO CSV')
            close = [a for a in ALLOWED if a.lower() == label.lower()]
            hint = f" (did you mean '{close[0]}'?)" if close else ""
            problems.append(f"'{label}' is not an allowed label{hint}")
    return problems


if __name__ == "__main__":
    found = validate(sys.argv[1:])
    print("OK" if not found else "\n".join(found))
    sys.exit(1 if found else 0)    # exit code 1 tells the agent the check failed
