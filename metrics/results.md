# Results (collected)

Definitions, windows and reproduction steps: [README.md](README.md).
Each section names the file its numbers come from.

## 1. Scope: new issues by form

Window: <2025-01-01> to <2026-10-31>. Source: `report_gaps.txt` (first block, "by form").

| Form | Issues | % |
|---|---|---|
| bug | 805 | 51% |
| **Total** | 1568 | 100% |

Takeaway: bug reports are the largest group, hence we will focus on it to first to view its effectiveness.

## 2. Template gaps in bug reports

Window: as above. Source: `report_gaps.txt` ("Bug-form reports", "Gaps", "What the reports with gaps look like now").

Bug-form reports: 805; with at least one gap: 204 (25%).

| Gap | Reports | % of bug reports |
|---|---|---|
| show_versions() placeholder left in | 64 | 8% |
| Installed Versions filled, but not with show_versions() output | 127 | 16% |
| Reproducible Example empty or filler | 9 | 1% |
| Reproducible Example has no code | 22 | 3% |
| Issue Description empty or filler | 7 | 1% |
| Expected Behavior empty or filler | 14 | 2% |

What happened to the reports with gaps (labels as of collection):

| Outcome | Reports | % of reports with gaps |
|---|---|---|
| labelled Needs Info | 11 | 5% |
| labelled Closing Candidate | 14 | 7% |
| closed as not planned | 3 | 1% |
| closed as completed | 164 | 80% |
| still labelled Needs Triage | 35 | 17% |

Takeaway: gaps are common but rarely chased; whether a gap matters is a judgement call.

## 3. Time to first maintainer action

Window: <2026-08-01> to <2026-10-31>, bug reports by outsiders. 

Source: `first_response_summary.txt`, per-issue rows in `first_response.csv`.

| Measure | Value |
|---|---|
| Bug reports by outsiders | 96 |
| With a maintainer action so far | 84 (88%) |
| Median wait | 25.2 h |
| 90th percentile | 4.9 days |
| Acted on within 1 day | 41 of 96 (43%) |
| Acted on within 7 days | 74 of 90 (82%) |

## 5. Backlog

Source: `first_response_summary.txt` ("Triage") and a website search.
https://github.com/pandas-dev/pandas/issues?q=is%3Aissue+%22This+issue+is+still+labeled+Needs+Triage%2C+which+means+it+needs+another+look+before+work+starts+%22+in%3Acomments+label%3ABug

| Measure | Value |
|---|---|
| Still untriaged after 7 days | 26 of 90 (29%) |
| Still untriaged after 30 days | 9 of 45 (20%) |
| Bug Issues with a `/take` refusal because of a triage label | 27 |

## Summary for DESIGN.md

- Bug reports were 805 of 1568 new issues (51%).
- Median wait for a first maintainer action: 25.2 h (4.9 days).
- 25% of bug reports had a gap in the template
- 27 bug issues had a `/take` refusal because of the triage being undone.

## Limitations

- Labels and text are as of the collection date: gaps later edited away are not counted.
- Section 4 uses a shorter window than sections 1 to 3, to keep API calls low.
- A gap does not always mean the information was needed.
- ONLY issues from github can be collected, so issues filed on other platforms are not included
- The `/take` search counts issues with at least one refusal, not individual refusals.