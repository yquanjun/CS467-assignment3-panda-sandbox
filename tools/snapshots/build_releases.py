#!/usr/bin/env python3
"""Build data/releases.json: every release of pandas, numpy and pyarrow with its date.
used to check if the reporter is testing with the latest version

Source: PyPI's Index API (the JSON form of https://pypi.org/simple/<package>/).
Run from the root of your sandbox repo:

    pip install packaging
    python tools/snapshots/build_releases.py
"""
import json
import urllib.request
from collections import defaultdict
from pathlib import Path

from packaging.utils import (
    InvalidSdistFilename,
    InvalidWheelFilename,
    parse_sdist_filename,
    parse_wheel_filename,
)

PACKAGES = ["pandas", "numpy", "pyarrow"]
OUT = Path("data/releases.json")


def index_files(package):
    """Return the list of files PyPI lists for a package (JSON Index API)."""
    req = urllib.request.Request(
        f"https://pypi.org/simple/{package}/",
        headers={"Accept": "application/vnd.pypi.simple.v1+json"},
    )
    with urllib.request.urlopen(req, timeout=60) as resp:
        return json.load(resp)["files"]


def version_of(filename):
    """Work out the version from a wheel or sdist filename; None for other files."""
    try:
        if filename.endswith(".whl"):
            return parse_wheel_filename(filename)[1]
        return parse_sdist_filename(filename)[1]
    except (InvalidWheelFilename, InvalidSdistFilename):
        return None  # old installers (.exe, .egg, ...) are skipped


def build(package):
    times = defaultdict(list)
    yanked = defaultdict(list)
    for f in index_files(package):
        version = version_of(f["filename"])
        uploaded = f.get("upload-time")
        if version is None or not uploaded:
            continue
        times[version].append(uploaded)
        yanked[version].append(bool(f.get("yanked")))
    rows = [
        {
            "version": str(v),
            "released": min(times[v]),             # first file upload = release date
            "prerelease": v.is_prerelease,
            "yanked": all(yanked[v]),
        }
        for v in times
    ]
    rows.sort(key=lambda r: r["released"])
    return rows


def main():
    out = {}
    for package in PACKAGES:
        rows = build(package)
        out[package] = rows
        last = rows[-1]
        print(f"{package}: {len(rows)} releases, latest {last['version']} on {last['released'][:10]}")
    OUT.parent.mkdir(exist_ok=True)
    OUT.write_text(json.dumps(out, indent=1) + "\n")
    print(f"wrote {OUT}")


if __name__ == "__main__":
    main()
