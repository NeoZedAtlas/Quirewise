#!/usr/bin/env python3
"""Report which public API functions carry a documentation comment.

The tool scans installed public headers, collects every declared entry point
(``qw_*``, ``pdg_*``, ``pdz_*``) and checks whether the declaration is
immediately preceded by a comment block. Blocks that start with ``/*!`` or
``/**`` are counted as Doxygen-style as well. It never changes files.

``--strict`` fails when any function is undocumented; ``--baseline`` fails when
the undocumented count grows past a pinned report, which lets the project ratchet
documentation coverage without freezing every header at once.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

FUNCTION_RE = re.compile(r"\b((?:qw|pdg|pdz)_[a-z0-9_]+)\s*\(")
DOC_START_RE = re.compile(r"/\*")
DOXYGEN_RE = re.compile(r"/\*[!*]")
DOC_END_RE = re.compile(r"\*/")


def declaration_lines(lines: list[str]) -> list[tuple[int, str]]:
    """Yield (index, name) for entry points declared outside comments."""
    found: list[tuple[int, str]] = []
    in_comment = False
    for index, line in enumerate(lines):
        stripped = line.strip()
        if in_comment:
            if DOC_END_RE.search(line):
                in_comment = False
            continue
        if stripped.startswith("/*") and "*/" not in stripped:
            in_comment = True
            continue
        if stripped.startswith("*") or stripped.startswith("//"):
            continue
        if stripped.startswith("#define"):
            continue
        for match in FUNCTION_RE.finditer(line):
            found.append((index, match.group(1)))
    return found


def doc_kind(lines: list[str], index: int) -> str:
    """Return "doxygen", "comment" or "none" for the declaration at ``index``."""
    cursor = index - 1
    while cursor >= 0 and not lines[cursor].strip():
        cursor -= 1
    if cursor < 0 or not DOC_END_RE.search(lines[cursor]):
        return "none"
    while cursor >= 0:
        if DOXYGEN_RE.search(lines[cursor]):
            return "doxygen"
        if DOC_START_RE.search(lines[cursor]):
            return "comment"
        cursor -= 1
    return "none"


def scan_header(path: Path) -> dict:
    text = path.read_text(encoding="utf-8", errors="replace")
    lines = text.splitlines()
    seen: set[str] = set()
    undocumented: list[str] = []
    documented = 0
    doxygen = 0
    for index, name in declaration_lines(lines):
        if name in seen:
            continue
        seen.add(name)
        kind = doc_kind(lines, index)
        if kind == "none":
            undocumented.append(name)
        else:
            documented += 1
            if kind == "doxygen":
                doxygen += 1
    return {
        "header": str(path),
        "functions": len(seen),
        "documented": documented,
        "doxygen": doxygen,
        "undocumented": undocumented,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--prefix", type=Path,
                        help="installed prefix containing include/")
    parser.add_argument("--workspace", type=Path,
                        help="workspace root; scans libraries/*/include")
    parser.add_argument("--json", type=Path)
    parser.add_argument("--strict", action="store_true",
                        help="exit 1 when any function lacks a doc block")
    parser.add_argument("--baseline", type=Path,
                        help="pinned JSON report; fail when the undocumented "
                             "count grows past it")
    args = parser.parse_args()

    roots: list[Path] = []
    if args.prefix:
        include = args.prefix / "include"
        if not include.is_dir():
            print(f"error: {include} is not a directory", file=sys.stderr)
            return 2
        roots = sorted(include.rglob("*.h"))
    elif args.workspace:
        for library in sorted((args.workspace / "libraries").iterdir()):
            include = library / "include"
            if include.is_dir():
                roots.extend(sorted(include.rglob("*.h")))
    else:
        parser.error("pass --prefix or --workspace")

    results = [scan_header(path) for path in roots]
    total_functions = sum(item["functions"] for item in results)
    total_documented = sum(item["documented"] for item in results)
    total_doxygen = sum(item["doxygen"] for item in results)
    total_undocumented = total_functions - total_documented

    for item in results:
        if item["functions"]:
            status = "ok" if not item["undocumented"] else f"{len(item['undocumented'])} missing"
            print(f"{item['header']}: {item['documented']}/{item['functions']} documented ({status})")
    print(f"total: {total_documented}/{total_functions} documented "
          f"({total_doxygen} Doxygen-style), {total_undocumented} undocumented")

    failed = False
    if args.baseline:
        baseline = json.loads(args.baseline.read_text(encoding="utf-8"))
        allowed = int(baseline.get("undocumented", 0))
        if total_undocumented > allowed:
            print(f"error: {total_undocumented} undocumented functions exceed "
                  f"the pinned baseline of {allowed}", file=sys.stderr)
            failed = True
        else:
            print(f"baseline: {total_undocumented} undocumented (pinned {allowed})")

    if args.json:
        args.json.parent.mkdir(parents=True, exist_ok=True)
        args.json.write_text(json.dumps({
            "total_functions": total_functions,
            "documented": total_documented,
            "doxygen": total_doxygen,
            "undocumented": total_undocumented,
            "headers": results,
        }, indent=2) + "\n", encoding="utf-8")

    if failed:
        return 1
    return 1 if args.strict and total_undocumented else 0


if __name__ == "__main__":
    raise SystemExit(main())
