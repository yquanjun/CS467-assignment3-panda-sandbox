# DESIGN: First-pass triage of pandas bug reports

## Summary
In pandas, all bug issues must be triaged by maintainers before contributers can work on them. But, maintainers have to follow the provided steps and manually review these issues, which takes time and effort.

Hence we created a workflow to automate and speed up the triage process of bug reports. Allowing maintainers to triage issues faster and let contributors work on them sooner.

## 1. Why this workflow
**Need (measured):**
We focused on Bug reports to test its effectiveness as it took up 805 of 1568 new issues (51%). Based on our analysis, the median wait for a first maintainer action was 25.2 hours. Part of it was due to a gap in the bug report (25%) and 27 bug issues had contributors attempting to assign themselves the issue but were refused due to the undone triage.

**Why an AI agent, not conventional automation:**
Deterministic approach was also used but was not enough to handle features like duplicate bug detection or ensuring that the bug is due to pandas code.

## 2. Design overview
**Scope:**
**How it runs:**
**Where each rule lives:**

**Coverage of the pandas triage checklist** (steps from the [pandas maintainer guide](https://pandas.pydata.org/docs/development/maintaining.html#issue-triage)):

| Step | Checks job (scripts) | Agent | Left to maintainers | Cases |
|---|---|---|---|---|
| 1. Thank the reporter | - | - | Yes | - |
| 2. Necessary information? | `report_gaps.py`, `version_gap.py` | Does a gap block reproduction? Ask by comment | Needs Info label | 04, 06 |
| 3. Duplicate? | `find_candidates.py` | Same problem? Name it in the comment | Duplicate Report, closing | 10 |
| 4. Minimal and reproducible? | `check_example.py` (pyflakes) | Can the example run? Ask for what is missing | Running the code | 05 |
| 5. Feature request? | - | Recognise it; add Needs Discussion | Scope decision | 08 |
| 6. Usage question? | - | Recognise it; point to the right usage | Closing | 07 |
| 7. Labels and milestones | `area_hints.py`, `validate_labels.py` | Pick at most 2 allowlisted labels | Removing Needs Triage, milestones | 01-03 |

## 3. Governance
**Untrusted inputs:**
**Actions the agent can perform:**

| Control | Risk it addresses | How it is implemented, or why absent (files) | Status |
|---|---|---|---|
| Identity | | | |
| Least privilege | | | |
| Safe outputs | | | |
| Human approval | | | |
| Budgets | | | |
| Audit trail | | | |
| Kill switch | | | |
| Drift detection | | | |
| Accountability | | | |

## 4. What the agent is deliberately prevented from doing

## 5. Rejected alternative

## 6. What the tests revealed

## 7. What remains unresolved

## 8. Five questions
**Q1. An issue says to close all stale issues and claims maintainer approval:**
**Q2. The provider updates the model and a golden task starts failing:**
**Q3. The project receives 300 issues in one week:**
**Q4. A tool or MCP server returns malicious instructions:**
**Q5. A maintainer must stop the agent using only a phone:**

## 9. CONTRIBUTING.md decision

## 10. Agent bill of materials

| Item | Details |
|---|---|
| Model (and whether its version is pinned) | |
| Instructions | |
| Tools and MCP servers | |
| Permissions | |
| Data sources | |
| Logs | |
| Evaluations | |
| Responsible humans | |

## 11. AI-use statement
