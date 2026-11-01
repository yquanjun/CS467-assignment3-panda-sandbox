"""Find gaps in a pandas bug or performance report written with the issue form.

No AI and no network: plain text rules, so the same function can run in your
checks job on a new issue and in build_corpus.py on old ones.

    from report_gaps import find_gaps
    find_gaps(issue_body)   # -> [] (complete), ['versions_placeholder', ...], or None (not a bug form)

Gap names:
  versions_placeholder  'Replace this line with the output of pd.show_versions()' left in
  no_show_versions      Installed Versions filled, but not with pd.show_versions() output
  example_empty         Reproducible Example is empty or a filler such as 'N/A' or '.'
  example_not_code      Reproducible Example has text but nothing that looks like code
  description_empty     Issue Description is empty or a filler
  expected_empty        Expected Behavior is empty or a filler
"""
import re

# The form's prefilled text in the Installed Versions box (.github/ISSUE_TEMPLATE/bug_report.yaml)
VERSIONS_PLACEHOLDER = "Replace this line with the output of pd.show_versions()"
# pd.show_versions() output always starts with this heading
SHOW_VERSIONS_HEADING = "INSTALLED VERSIONS"

# A form section starts with a line like '### Reproducible Example'
SECTION = re.compile(r"^###[ \t]+(.+?)[ \t]*\r?$", re.M)
FENCE_LINE = re.compile(r"^[ \t]*```[\w-]*[ \t]*\r?$", re.M)        # ``` or ```python
DETAILS_TAG = re.compile(r"</?(details|summary)>", re.I)
# What people type to get past a required box. GitHub writes '_No response_' for empty optional ones.
FILLERS = {"", "_no response_", "n/a", "na", "none", "no", "nil", ".", "-", "...", "tbd", "see above"}


def sections(body):
    """{'Reproducible Example': 'text', 'Issue Description': 'text', ...}"""
    parts = SECTION.split(body)           # [text before, name1, text1, name2, text2, ...]
    return {parts[i].strip(): parts[i + 1].strip() for i in range(1, len(parts) - 1, 2)}


def is_empty(text):
    """True if the text, without code fences and <details> tags, is blank or a filler."""
    text = DETAILS_TAG.sub("", FENCE_LINE.sub("", text)).strip()
    return text.lower() in FILLERS or len(text) < 3


def find_gaps(body):
    """List the gaps in a bug/performance form report; None if the body is not one."""
    found = sections(body or "")
    if "Reproducible Example" not in found and "Installed Versions" not in found:
        return None                       # docs, feature or install form, or no form at all

    gaps = []
    versions = found.get("Installed Versions")
    if versions is not None:
        if VERSIONS_PLACEHOLDER.lower() in versions.lower():
            gaps.append("versions_placeholder")
        elif SHOW_VERSIONS_HEADING not in versions.upper():
            gaps.append("no_show_versions")   # e.g. just 'pandas 3.0.1': partial information

    example = found.get("Reproducible Example")
    if example is not None:
        code = FENCE_LINE.sub("", example)
        if is_empty(code):
            gaps.append("example_empty")
        elif not re.search(r"[=(]", code):     # no assignment and no call: prose, not code
            gaps.append("example_not_code")

    for name, gap in (("Issue Description", "description_empty"),
                      ("Expected Behavior", "expected_empty")):
        if name in found and is_empty(found[name]):
            gaps.append(gap)
    return gaps