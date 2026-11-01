"""Static checks on a bug report's Reproducible Example. Nothing is executed.

    from check_example import check_example
    check_example(body)  ->  {
        "found": True,                    # is there an example to check at all?
        "parsed": "whole" | "partial" | "no",   # did the code parse as Python?
        "undefined_names": ["outfile"],   # names used but never defined (pyflakes)
        "missing_imports": ["pd"],        # the usual aliases used without an import
        "local_files": ["data.csv"],      # reads of files only the reporter has
        "urls": [],                       # reads from the internet
        "traceback_only": False,          # the box holds a traceback, not code
        "pyflakes": "ok" | "not installed",
    }

The agent judges what the findings mean: a missing 'import pandas as pd' is trivial,
an undefined variable that holds the data is not.

How it works, in order:
  1. take the Reproducible Example box (or, with no form, every ``` block in the issue);
  2. look at each ``` block separately, drop '>>>' prompts and anything after a traceback,
     and skip blocks that are only output;
  3. keep the block if it parses as Python, otherwise its longest run of lines that does
     ('parsed' says which);
  4. run pyflakes on the kept code and sort the undefined names into small slips
     (missing_imports) and real gaps (undefined_names);
  5. look for reads of files or URLs given as plain strings.

    python check_example.py < issue_body.md      # prints the result as JSON
"""
import ast
import json
import re
import sys
import textwrap

from report_gaps import bug_sections, form_type

# A fence line on its own: ``` or ```python
FENCE = re.compile(r"^[ \t]*```[\w-]*[ \t]*$", re.M)
# A complete ``` ... ``` block; group 1 is what is inside it
CODE_BLOCK = re.compile(r"```[\w-]*[ \t]*\n(.*?)```", re.S)
# Interactive prompts: '>>> ', '... ' (Python shell) and 'In [1]: ' (IPython/Jupyter)
PROMPT = re.compile(r"^\s*(?:>>>|\.\.\.|In \[\d+\]:)\s?", re.M)
# Signs of a pasted traceback: its first line, a 'File "...", line N' line, or such a line
# cut short at the front (e.g. 'andas/compat/_optional.py", line 135, in ...')
TRACEBACK = re.compile(r"Traceback \(most recent call last\)|^\s*File \".*\", line \d+"
                       r"|\", line \d+, in \S", re.M)
# A line that starts like code: an import, an assignment (not '=='), or a call 'name('.
# Used on stripped lines, so indented code counts too.
CODE_LINE = re.compile(r"^(?:import |from \S+ import |[A-Za-z_][\w.\[\]'\"]*\s*=[^=]|[A-Za-z_][\w.]*\()")
MAX_LINES = 200            # longest_run tries up to n*n/2 pieces; cap n to keep it fast

# Aliases everyone recognises; using one without importing it is a small slip, not a blocker.
COMMON_ALIASES = {"pd", "np", "plt", "pa", "pq", "sns", "mpl", "dt", "datetime", "io", "os",
                  "math", "random", "time", "pandas", "numpy", "pyarrow", "matplotlib"}

# Calls that read data, with a plain string as the first argument:
#   read_csv("x.csv"), open(r"C:\data.txt"), read_parquet(path="s3://...")
# group 1 = the quote character, group 2 = the file name or URL.
# The (?!...) at the end skips files opened for writing: open("out.txt", "w"/"wb"/"a"/"x").
READERS = re.compile(
    r"\b(?:read_\w+|open|load|loadtxt|genfromtxt|ExcelFile|HDFStore|ParquetFile)\s*\(\s*"
    r"(?:[a-z_]+\s*=\s*)?[rRbBfF]?(['\"])([^'\"\n]+)\1(?!\s*,\s*['\"][wax])")


def example_text(body):
    """The text of the Reproducible Example section, or every code block when there is no form."""
    if form_type(body or "") == "bug":
        # bug_sections keeps '###' headings pasted inside the box as part of the box
        return bug_sections(body).get("Reproducible Example", "")
    return "\n\n".join(CODE_BLOCK.findall(body or ""))


def strip_prompts(code):
    """Keep only the input lines of a '>>>' or 'In [1]:' session (output lines have no
    prompt, so they are dropped). Code without prompts is returned unchanged."""
    if not PROMPT.search(code):
        return code
    return "\n".join(PROMPT.sub("", line) for line in code.splitlines() if PROMPT.match(line))


def parses(code):
    """True if the text is valid Python syntax. ast.parse only reads it; nothing runs."""
    try:
        ast.parse(code)
        return True
    except (SyntaxError, ValueError):       # ValueError: e.g. a null byte in the text
        return False


def longest_run(code):
    """The longest run of consecutive lines that parses as Python (dedented), or ''.

    Tries every start line and, for each, the longest piece first. Two shortcuts:
    once a piece is no longer than the best so far, shorter ones from this start cannot
    win; and the first piece that parses is the longest from this start."""
    lines = code.splitlines()
    best = ""
    for start in range(len(lines)):
        for end in range(len(lines), start, -1):
            # dedent: code indented in the box (e.g. by 4 spaces) becomes top-level code
            piece = textwrap.dedent("\n".join(lines[start:end])).strip("\n")
            if len(piece) <= len(best):
                break
            # must contain '=' or '(': a bare word like 'Output' is valid Python but not code
            if re.search(r"[=(]", piece) and parses(piece):
                best = piece
                break
    return best


def blocks(text):
    """Each ``` block on its own (code and pasted output are often in separate blocks);
    the whole text when it has no complete block."""
    found = CODE_BLOCK.findall(text)
    return found if found else [text]


def before_traceback(block):
    """The part of a block before a pasted traceback (code and its error often share a box)."""
    match = TRACEBACK.search(block)
    return block[:match.start()] if match else block


def is_output(block):
    """A block that holds only printed output or an error message, with no line of code:
    True when NO line starts like code (see CODE_LINE)."""
    return not any(CODE_LINE.match(line.strip()) for line in block.splitlines())


def code_chunks(text):
    """('whole' | 'partial' | 'no', [pieces of code]). A block that parses is used whole;
    otherwise the longest run of lines in it that parses (examples often mix prose, output
    and code in one box). Blocks with no line of code (tracebacks, output) are skipped."""
    status, chunks = [], []
    for block in blocks(text):
        # clean the block: no fence lines, no prompts, nothing from the traceback onwards
        code = before_traceback(strip_prompts(FENCE.sub("", block))).strip("\n")
        code = "\n".join(code.splitlines()[:MAX_LINES])
        if not code.strip() or is_output(code):
            continue                                   # nothing that looks like code
        if parses(code):
            status.append("whole")
            chunks.append(code)
            continue
        best = longest_run(code)                       # code mixed with prose or output
        status.append("partial" if best else "no")
        if best:
            chunks.append(best)
    if not chunks:
        return "no", []
    # 'whole' only if every code block parsed completely
    return ("whole" if all(s == "whole" for s in status) else "partial"), chunks


def undefined_names(code):
    """Names pyflakes reports as undefined (one entry per use). None when pyflakes is not
    installed, so the report can say so instead of failing."""
    try:
        from pyflakes import api, messages, reporter
    except ImportError:
        return None

    # pyflakes normally prints its findings; this reporter collects only 'undefined name'
    # findings and ignores the rest (unused imports, syntax errors, ...)
    class Collect(reporter.Reporter):
        def __init__(self):
            self.found = []

        def flake(self, message):
            if isinstance(message, messages.UndefinedName):
                self.found.append(message.message_args[0])

        def unexpectedError(self, *args):
            pass

        def syntaxError(self, *args):
            pass

    collect = Collect()
    api.check(code, "example.py", collect)       # static analysis only; nothing runs
    return collect.found


def check_example(body):
    text = example_text(body)
    # 'found': is there anything in the box once the ``` lines are removed? The bug form
    # wraps the box in ```python ... ``` itself, so an empty box is just fence lines.
    result = {"found": bool(FENCE.sub("", text).strip()), "parsed": "no", "undefined_names": [],
              "missing_imports": [], "local_files": [], "urls": [],
              "traceback_only": False, "pyflakes": "ok"}
    if not result["found"]:
        return result

    # check if there is code
    parsed, chunks = code_chunks(text)
    result["parsed"] = parsed
    if not chunks and TRACEBACK.search(text):
        result["traceback_only"] = True          # nothing to check: no code, only an error
        return result
    names = []

    # find undefined names/vars/imports (each name once, in the order first seen)
    for chunk in chunks:
        found = undefined_names(chunk)
        if found is None:
            result["pyflakes"] = "not installed"
            break
        for name in found:
            if name not in names:
                names.append(name)
    # small slips (a forgotten 'import pandas as pd') vs real gaps (the reporter's own
    # variables, e.g. the data, that are never defined); at most 10 to keep the report short
    result["missing_imports"] = [n for n in names if n in COMMON_ALIASES]
    result["undefined_names"] = [n for n in names if n not in COMMON_ALIASES][:10]

    # files/url checks: data the example reads from somewhere only the reporter can reach.
    # If no code was found, scan the raw text instead.
    for chunk in chunks or [text]:
        for _, target in READERS.findall(chunk):
            if "\n" in target or "{" in target or ("," in target and len(target) > 40):
                continue                    # inline data or a computed name, not a file name
            kind = "urls" if re.match(r"(https?|s3|gs|ftp)://", target) else "local_files"
            if target not in result[kind]:
                result[kind].append(target[:100])
    return result


if __name__ == "__main__":
    print(json.dumps(check_example(sys.stdin.read()), indent=1))
