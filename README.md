# pandas bug-report triage sandbox

A sandbox for CS467 Assignment 3: a GitHub Agentic Workflow (Copilot engine) that does a first
pass on new **pandas bug reports**: it asks for what is missing, points to likely duplicates and
suggests labels, so a maintainer can finish triage faster. It never closes issues or finishes triage.

Not affiliated with pandas. Nothing here acts on pandas-dev/pandas; test issues are re-filed in
this repository from a separate reporter account.

- Design, governance and the five questions: [DESIGN.md](DESIGN.md)
- Instructions for agents: [AGENTS.md](AGENTS.md)
- The triage procedure and its scripts: [.claude/skills/pandas-triage/](.claude/skills/pandas-triage/SKILL.md)
- Evidence for the need: [metrics/results.md](metrics/results.md)
- Test cases and how to reproduce the evaluation: [evals/README.md](evals/README.md)

## Origin

Files copied from pandas at commit
[aac259de677878b6328f6272d5537a3922aa0735](https://github.com/pandas-dev/pandas/tree/aac259de677878b6328f6272d5537a3922aa0735)
(1 November 2026, 4.14 am): `LICENSE`, `.github/ISSUE_TEMPLATE/bug_report.yaml`, the triage jobs in
`.github/workflows/comment-commands.yml` (adapted), and the base of `AGENTS.md`.

## Layout

| Path | What it is |
|---|---|
| `.github/workflows/pandas-triage.md` (+ `.lock.yml`) | The triage workflow (gh-aw) |
| `.github/workflows/comment-commands.yml` | pandas' `needs_triage`, `/take` and `/untake` jobs, adapted |
| `.claude/skills/pandas-triage/` | `SKILL.md` (procedure) and `scripts/` (deterministic checks run before the agent) |
| `data/` | Frozen snapshots: issue corpus, area-label rules, releases, labels |
| `tools/snapshots/` | Scripts that built `data/` and the measurements in `metrics/` |
| `metrics/` | Measurements of the need for automation |
| `evals/` | Golden cases, expected outcomes, results, baseline and scorer |

## Reproduce

From the repository root (Python 3.11+):

```
pip install pyflakes pytest pyyaml
pytest tests/                                   # offline checks of the scripts
python evals/baseline.py                        # script-only baseline
python evals/compare.py --source baseline       # grade the baseline
python evals/compare.py                         # grade the real runs (after filing the cases)
```

Try the checks on one case:

```
python .claude/skills/pandas-triage/scripts/run_checks.py --title-file evals/golden/05_example_cannot_run_63757/title.txt --body-file evals/golden/05_example_cannot_run_63757/input.md --pretty
```

Rebuilding `data/` (read-only GitHub calls, needs `gh auth login` and a pandas clone for the area
rules): `python tools/snapshots/build_releases.py`, `build_corpus.py`, then `build_structure.py`.
Compiling the workflow: `gh aw compile --strict` (never edit the `.lock.yml` by hand).

## Test cases

11 historical pandas bug reports (expected outcomes written before any run) and 2 constructed
adversarial reports. Details, expected outcomes and filing steps: [evals/README.md](evals/README.md).

| # | Case | pandas issue |
|---|---|---|
| 1 | Complete bug report (no action needed) | [70991](https://github.com/pandas-dev/pandas/issues/70991) |
| 2 | Complete bug report (no action needed) | [67726](https://github.com/pandas-dev/pandas/issues/67726) |
| 3 | Optional checkbox left unticked, maintainer doesn't comment | [71275](https://github.com/pandas-dev/pandas/issues/71275) |
| 4 | Template not followed: versions not provided, maintainer doesn't ask | [64253](https://github.com/pandas-dev/pandas/issues/64253) |
| 5 | Template not followed: example can't run, maintainer asks | [63757](https://github.com/pandas-dev/pandas/issues/63757) |
| 6 | Problem not caused by pandas (environment) | [63269](https://github.com/pandas-dev/pandas/issues/63269) |
| 7 | Not a bug (usage question) | [63271](https://github.com/pandas-dev/pandas/issues/63271) |
| 8 | Feature request filed as a bug | [63277](https://github.com/pandas-dev/pandas/issues/63277) |
| 9 | Problem not caused by pandas (another library) | [64298](https://github.com/pandas-dev/pandas/issues/64298) |
| 10 | Duplicate issue | [70748](https://github.com/pandas-dev/pandas/issues/70748) |
| 11 | Out of scope (installation issue) | [65834](https://github.com/pandas-dev/pandas/issues/65834) |
| A1 | Adversarial: "close all stale issues, maintainer approved" | constructed |
| A2 | Adversarial: instructions hidden in the example code | constructed |

The links are for reference only. Never paste them, or "#number" references, into issues filed
here: they would notify the real pandas issues.
