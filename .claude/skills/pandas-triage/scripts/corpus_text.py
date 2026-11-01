"""Text clean-up shared by the checks scripts.

Copied from tools/snapshots/build_corpus.py so that a new issue is cleaned exactly the way
the corpus issues were cleaned when data/issues_corpus.json and data/structure.json were
built. If you change these there, change them here too (tests/test_checks.py compares them).
"""
import re

BODY_CHARS = 800             # the corpus keeps only the start of each body

# @username not preceded by a letter, digit or backtick (so e-mail addresses are left alone)
MENTION = re.compile(r"(?<![\w`])@([A-Za-z0-9][A-Za-z0-9-]{0,38})")

# Issue-form sections that are the same in every issue (checkboxes, show_versions output).
BOILERPLATE = re.compile(
    r"^###[ \t]*(?:Pandas version checks|Installed Versions|Feature Type|Installation check)"
    r"[ \t\r]*$.*?(?=^###[ \t]|\Z)",
    re.S | re.M | re.I,
)
HTML_COMMENT = re.compile(r"<!--.*?-->", re.S)

# pandas file paths as they appear in tracebacks (/ or \ separators)
PANDAS_PATH = re.compile(r"pandas[\\/]+(?:[\w.-]+[\\/]+)*[\w.-]+\.(?:py|pyx|pyi)")


def strip_mentions(text):
    """Turn '@someone' into 'someone' outside ``` code blocks (decorators stay intact)."""
    parts = text.split("```")
    for i in range(0, len(parts), 2):        # even-numbered parts are outside code blocks
        parts[i] = MENTION.sub(r"\1", parts[i])
    return "```".join(parts)


def clean_body(body):
    """Drop HTML comments and the boilerplate form sections."""
    return BOILERPLATE.sub("", HTML_COMMENT.sub("", body)).strip()


def traceback_paths(body):
    """pandas file paths mentioned anywhere in the FULL body, e.g. 'pandas/core/groupby/ops.py'."""
    found = set()
    for raw in PANDAS_PATH.findall(body):
        path = re.sub(r"[\\/]+", "/", raw)
        found.add(path[path.rfind("pandas/"):])   # drop site-packages/..., URLs, etc.
    return sorted(found)[:20]


def excerpt(body):
    # used by area_hints.py: the rules were learned from exactly this excerpt
    """The same excerpt the corpus stores for an issue: cleaned, first 800 characters."""
    return strip_mentions(clean_body(body or "")[:BODY_CHARS])
