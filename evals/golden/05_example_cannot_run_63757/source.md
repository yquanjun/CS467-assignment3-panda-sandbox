# 05_example_cannot_run_63757

- Upstream: pandas issue 63757 (plain text on purpose: no links in issues)
- Opened: 2026-01-19T16:20:16Z; reporter association: NONE
- Original title: BUG:
- Current title: BUG: inconsistent date string conversion leads to large downstream performance degradation.   (renamed)
- Body: edited 2 time(s): earliest of 3 revisions used
- Labels at opening (form): Bug, Needs Triage
- Labels added later by others: 2026-10-14 Datetime; 2026-10-14 Usage Question; 2026-10-14 IO CSV
- Labels now: Datetime, Usage Question, IO CSV
- State now: CLOSED (COMPLETED)

## Maintainer responses (evidence for expected.yaml)

**2026-10-14, member:**

> Checking more samples goes against [PDEP-4](https://pandas.pydata.org/pdeps/0004-consistent-to-datetime-parsing.html), which I do not think there is an appetite to revisit. Specify `date_format="ISO8601"` to get good performance.
> 
> Closing.

Closed 2026-10-14 (COMPLETED).
