"""Compare the pandas version in a report with the latest release before a date.

    from version_gap import version_gap
    version_gap(body, "2026-02-20T11:45:45Z")  ->  {
        "reported": "3.0.1",
        "source": "installed_versions" | "text" | None,
        "latest_on_date": "3.0.1",      # latest final release before the date (data/releases.json)
        "status": "latest" | "behind_patch" | "behind_minor" | "behind_major"
                  | "dev_or_newer" | "unknown",
    }

    python version_gap.py 2026-02-20T11:45:45Z < issue_body.md
"""
import json
import re
import sys
from pathlib import Path

from report_gaps import sections

ROOT = Path(__file__).resolve().parents[4]          # repository root
RELEASES = ROOT / "data" / "releases.json"

# A pandas version: 2.2, 3.0.1, 3.0.0rc0, 3.2.0.dev0+131.g48f2692dd9 (a build of main)
VERSION = r"(\d+\.\d+(?:\.\d+)?(?:(?:rc|\.dev|dev|a|b)\d*(?:\+[\w.]+)?)?)"
# Where reporters give the version, most reliable first:
#   'pandas                : 3.0.1'   a line of pd.show_versions() output
#   'Name: pandas / Version: 2.3.3'   output of `pip show pandas`
#   'pandas 3.0.1', 'pandas==3.0.1', 'pandas version 3.0.1'   in the text
IN_SHOW_VERSIONS = re.compile(r"^\s*pandas\s*:\s*" + VERSION, re.M | re.I)
IN_PIP_SHOW = re.compile(r"Name:\s*pandas\s*\n\s*Version:\s*" + VERSION, re.I)
IN_TEXT = re.compile(r"\bpandas(?:\s*(?:==|version|v)\s*|\s+)" + VERSION, re.I)


def reported_version(body):
    """(version, where it was found) or (None, None). show_versions output wins over
    a version mentioned in the text."""
    body = body or ""
    versions = sections(body).get("Installed Versions", "")
    match = IN_SHOW_VERSIONS.search(versions) or IN_SHOW_VERSIONS.search(body)
    if match:
        return match.group(1), "installed_versions"
    match = IN_PIP_SHOW.search(body) or IN_TEXT.search(body)
    if match:
        return match.group(1), "text"
    return None, None


def release_tuple(version):
    """'3.0.1' -> (3, 0, 1); '2.2' -> (2, 2, 0)."""
    # only the numbers count: '3.0.1rc0' -> (3, 0, 1); missing parts are 0
    numbers = [int(n) for n in re.match(r"\d+(?:\.\d+)*", version).group(0).split(".")[:3]]
    return tuple(numbers + [0] * (3 - len(numbers)))


def latest_before(when, releases=None):
    """The newest final, non-yanked pandas release published before `when` (ISO date)."""
    # release dates are ISO strings, so '<' compares them as dates
    if releases is None:
        releases = json.loads(RELEASES.read_text(encoding="utf-8"))["pandas"]
    final = [r for r in releases
             if not r["prerelease"] and not r["yanked"] and r["released"] < when]
    return max(final, key=lambda r: release_tuple(r["version"]))["version"] if final else None


def version_gap(body, when, releases=None):
    reported, source = reported_version(body)
    latest = latest_before(when, releases)
    result = {"reported": reported, "source": source, "latest_on_date": latest, "status": "unknown"}
    if not reported or not latest:
        return result
    # a development build (main branch) or a release candidate: newer than any release
    if re.search(r"dev|rc|a\d|b\d|\+", reported):
        result["status"] = "dev_or_newer"
        return result
    mine, newest = release_tuple(reported), release_tuple(latest)
    if mine >= newest:
        result["status"] = "latest" if mine == newest else "dev_or_newer"
    # compare major, then minor, then patch: (2, 2, 3) vs (2, 3, 3) -> behind_minor
    elif mine[0] < newest[0]:
        result["status"] = "behind_major"
    elif mine[1] < newest[1]:
        result["status"] = "behind_minor"
    else:
        result["status"] = "behind_patch"
    return result


if __name__ == "__main__":
    print(json.dumps(version_gap(sys.stdin.read(), sys.argv[1]), indent=1))
