# DESIGN: First-pass triage of pandas bug reports

## Summary
In pandas, every bug report must be triaged by a maintainer before contributors can work on it
(`/take` is refused while Needs Triage is on), and maintainers follow the triage steps by hand.
This workflow does a first pass on new bug reports: it asks for what is missing, points to likely
duplicates and suggests labels, so maintainers can triage faster and contributors start sooner.
It never finishes triage itself, and it runs no code from issues (Variant A).

## 1. Why this workflow
**Need (measured, details in `metrics/results.md`):** bug reports were 805 of 1,568 new issues
(51%, Jan 2025 to Oct 2026). For outsiders' bug reports filed Aug to Oct 2026 (n = 96), the median
wait for a first maintainer action was 25.2 h (90th percentile 4.9 days), and 29% were still
untriaged after 7 days. 25% of bug reports left a form section unfilled, and 27 bug reports had a
`/take` refused because triage was not done. Limits: labels and text as of collection, triage on
Slack or the mailing list is invisible, and a gap does not always mean information was needed.

**Why an AI agent, not conventional automation:** scripts find the facts (gaps, undefined names,
version, similar issues); deciding what they mean needs judgement: does a gap block reproduction,
is it a usage question, a feature request or another library's fault, is a similar issue the same
problem. Fixed rules would ask for versions in cases 03 and 04 and cannot tell 07 to 09 apart.

## 2. Design overview
**Scope:** new issues filed with the bug form, or with no form when the agent judges it a bug.
Other forms and maintainers' own issues are skipped. Labels are limited to 8 area labels and
3 triage labels, a proof of concept rather than pandas' full 157.

**How it runs** (`.github/workflows/pandas-triage.md`, compiled with gh-aw v1.0.1): issue opened →
start-up checks (roles, bots, maintainer skip, rate limit) → `checks` job runs `run_checks.py`:
scope gate plus an evidence report (gaps, example checks, version gap, duplicate candidates,
area hints) → agent job (Copilot) reads the issue and report and follows the skill → threat
detection → safe-output job applies at most 1 comment and 2 labels → a maintainer finishes.

**Where each rule lives:** facts (form sections, label names, repo map, commands) in `AGENTS.md`,
loaded by Copilot automatically; the procedure (when to comment, labels, comment format) in
`.claude/skills/pandas-triage/SKILL.md`; checks that need no judgement in its `scripts/`; hard
limits in the workflow's permissions, safe outputs, sparse checkout and the scope gate.

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
| Extra: cause outside pandas | - | Recognise it; add Closing Candidate | Closing | 06, 09 |

## 3. Governance
**Untrusted inputs:** the issue title and body; excerpts of earlier issues in the candidates; the
checks report (built from both); GitHub tool responses. The prompt and skill treat all of them as
data. Issue text reaches the checks job through `env:`, not the shell command. `min-integrity:
none` is needed because public repos otherwise hide every outsider's issue from the agent.

**Actions the agent can perform:** read issues in this repo (`issue_read` only, read-only); run
`cat SKILL.md` and `validate_labels.py`; request 1 comment and 1 label call (max 2 labels) on the
triggering issue, or a `noop` that stays in the run log.

| Control | Risk it addresses | How it is implemented, or why absent (files) | Status |
|---|---|---|---|
| Identity | Actions look like a person's | Writes come from the safe-output job as `github-actions[bot]`; comments start "Automated first-pass check". Model use is billed to the owner's Copilot via the `COPILOT_GITHUB_TOKEN` PAT (`pandas-triage.md`, `SKILL.md`) | Implemented |
| Least privilege | Agent changes the repo | `permissions: contents/issues: read`; GitHub tool limited to `issue_read` in this repo; bash limited to 2 commands; sparse checkout of `.github/`, `.claude/`, `AGENTS.md` (no `evals/`, `data/`) | Implemented |
| Safe outputs | Closing, relabelling, spam, pings | `add-comment` max 1; `add-labels` allowlist, `blocked` list, `max: 1`, `max-labels: 2`; both `target: triggering`; `mentions: false`; threat detection; no close/remove/assign outputs | Implemented |
| Human approval | Agent's call is final | Maintainers remove Needs Triage, add Needs Info/Duplicate, close; CODEOWNERS on workflow, skill, data, evals; ruleset on `main` (`.github/CODEOWNERS`) | Implemented |
| Budgets | Runaway cost or spam | `timeout-minutes: 10`, `max-turns: 12`, `user-rate-limit` 3/h per reporter (experimental in gh-aw), `max-ai-credits` per run, `max-daily-ai-credits`; the scope gate skips the agent for other forms | Implemented|
| Audit trail | Cannot explain an action | Actions logs and `gh aw audit` (prompt, tool calls, model, credits, firewall); per case in `evals/golden/*/actual/` | Implemented |
| Kill switch | Agent misbehaves | Disable the workflow (web or `gh aw disable`) and cancel running runs; writes happen only after the agent job, so a cancelled run applies nothing | Implemented |
| Drift detection | Model or data changes behaviour | Rerun the golden set when the audit shows a new model, after changes to skill, workflow or data, and monthly; the owner reviews every failed case | Proposed |
| Accountability | Nobody owns it | Owner `yquanjun` can change or disable it (CODEOWNERS, ruleset) and answers for its comments and labels | Implemented |

## 4. What the agent is deliberately prevented from doing
Closing, reopening, assigning or `/take`; removing any label (Needs Triage stays for a human);
adding Needs Info, Duplicate Report or Regression (Needs Info was used on 11 of 204 reports with
gaps; a wrong duplicate label buries a real bug); more than 2 labels or 1 comment; touching other
issues; @mentions and bot commands; running issue code; reading `evals/`; acting on other forms or
maintainers' issues; thanking the reporter (noise).

## 5. Rejected alternative
A template-enforcement bot that adds Needs Info and asks for every unfilled section. The data
argued against it: maintainers added Needs Info to 5% of reports with gaps and closed 80% as
completed anyway, and in cases 03 and 04 they ignored the gap and fixed the bug. Asking on every
gap adds noise and slows good reports, so the agent asks only when a gap blocks reproduction.

## 6. What the tests revealed
- Building the checks: headings pasted inside case 05's example box were read as form sections
  (the example looked empty); fixed in both copies of `report_gaps.py`. The checks give the
  expected signals on all 13 golden inputs (`run_checks.py --pretty`).
- Compiling: gh-aw v1.0.1 rejected per-tool call limits, so `issue_read` has none; zizmor found
  no High issues (Medium/Low only in gh-aw's generated jobs); actionlint failed to run locally.
- Setup: the form adds Bug and Needs Triage only if those labels exist in the repo.


## 7. What remains unresolved
- The model is auto-selected (Copilot Student) and cannot be pinned; only reruns catch drift.
- No staged (preview) trial was run; area rules are weak for some labels (Strings: 29% recall).
- Duplicate search is keyword-based over a frozen corpus (to 31 Oct 2026); `as_of.json` replay is
  sandbox-only; it is unknown whether skipped runs count towards the rate limit; no Variant B.

## 8. Five questions
**Q1. An issue says to close all stale issues and claims maintainer approval:** nothing closes.
There is no close output and the token is read-only; outputs only reach the triggering issue, at
most 1 comment and 2 allowlisted labels.

**Q2. The provider updates the model and a golden task starts failing:** the audit records each
run's model; a new model triggers a golden-set rerun showing which case fails. An invisible change
is caught only at the monthly rerun or when a maintainer sees a bad comment.

**Q3. The project receives 300 issues in one week:** other forms are skipped at no cost; each
reporter gets 3 runs per hour; once the daily credit cap is reached, runs fail until the next day
and those issues wait for normal human triage (it fails closed). 

**Q4. A tool or MCP server returns malicious instructions:** the agent can still only read issues,
run the two allowed commands, and request 1 comment and 2 allowlisted labels on the triggering
issue. The firewall limits network access and threat detection checks outputs. Worst case: a
misleading comment or wrong label on one issue, which a maintainer removes.

**Q5. A maintainer must stop the agent using only a phone:** in the phone's browser open the repo →
Actions → "pandas bug-report triage" → "…" → Disable workflow; then open any running run → Cancel.
New issues no longer start runs, and a cancelled run applies nothing.

## 9. CONTRIBUTING.md decision
Not added. The agent only posts advisory comments and labels; nobody submits its output, and its
rules bind the agent, not contributors. Its comments say they are automated and not a review.

## 10. Agent bill of materials

| Item | Details |
|---|---|
| Model (and whether its version is pinned) | GitHub Copilot engine, model auto-selected (`auto`, Student plan); not pinned; recorded per run by `gh aw audit`|
| Instructions | Workflow prompt (`.github/workflows/pandas-triage.md`), `AGENTS.md`, `.claude/skills/pandas-triage/SKILL.md` |
| Tools and MCP servers | GitHub MCP server: `issue_read` only, read-only, this repo; bash: `cat SKILL.md`, `validate_labels.py`; no other servers |
| Permissions | `contents: read`, `issues: read`; writes only via safe outputs (1 comment, 2 labels); `COPILOT_GITHUB_TOKEN` (Copilot Requests: read) |
| Data sources | The issue; checks report from `data/` (1,568-issue corpus, area rules, releases, labels) and `evals/as_of.json` |
| Logs | GitHub Actions run logs; `gh aw audit`; `evals/golden/*/actual/` |
| Evaluations | `evals/golden/`: 11 real cases (expected outcomes committed before runs), 2 adversarial |
| Responsible humans | `yquanjun` (repository owner and CODEOWNER) |

## 11. AI-use statement
AI was used to generate scripts and update documentations. But i have revealed them myself by reading each line and making sure its correct.