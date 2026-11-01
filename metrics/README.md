# Measuring the need

All data is public pandas-dev/pandas data, read-only. Scripts are in tools/snapshots/.
Results change as issues are edited and relabelled.

## Windows
- Corpus window (scope, gaps, Needs Info): <2025-01-01> to <2026-10-31>
- Timeline window (wait times, backlog): <2026-08-01> to <2026-10-31>
  (shorter because reading each issue's timeline costs one API call per issue)

## Definitions
- Gap: a bug-form section left unfilled, as found by report_gaps.py (six gap types).
- Triaged: a person removed the Needs Triage label


## Files
 
| File | Made by |
|---|---|
| `report_gaps.txt` | `measure_report_gaps.py` |
| `needs_info_history.txt` | `find_label_history.py --bug-only` |
| `first_response_summary.txt`, `first_response.csv` | `measure_first_response.py` |
| `results.md` | Filled in by hand from the files above |

## Reproduce
- Fetch issues data and store it in the corpus: python tools/snapshots/build_corpus.py
- Use the corpus data to measure gaps: python tools/snapshots/measure_report_gaps.py | Out-File -Encoding utf8 metrics/report_gaps.txt
- Measure the first response time: python tools/snapshots/measure_first_response.py | Out-File -Encoding utf8 metrics/first_response_summary.txt

## Limitations
- Labels and text are as of the collection date: gaps later edited away are not counted
- ONLY issues from github can be collected, so issues filed on other platforms are not included