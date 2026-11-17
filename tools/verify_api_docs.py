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


def comment_spans(text: str) -> list[tuple[int, int]]:
    """Return (start, end) offsets of /* ... */ comment blocks."""
    spans: list[tuple[int, int]] = []
    cursor = 0
    while True:
        start = text.find("/*", cursor)
        if start < 0:
            break
        end = text.find("*/", start + 2)
        if end < 0:
            spans.append((start, len(text)))
            break
        spans.append((start, end + 2))
        cursor = end + 2
    return spans


def declaration_start(text: str, position: int) -> int:
    """Return the offset where the declaration containing position starts."""
    last_sep = max(text.rfind(";", 0, position),
                   text.rfind("{", 0, position),
                   text.rfind("}", 0, position))
    last_comment = text.rfind("*/", 0, position)
    cursor = last_comment + 2 if last_comment > last_sep else last_sep + 1
    while cursor < position and text[cursor].isspace():
        cursor += 1
    return cursor


def declaration_entries(text: str) -> list[tuple[int, str]]:
    """Yield (offset, name) for entry points declared outside comments."""
    spans = comment_spans(text)
    found: list[tuple[int, str]] = []
    for match in FUNCTION_RE.finditer(text):
        offset = match.start()
        if any(start <= offset < end for start, end in spans):
            continue
        line_start = text.rfind("\n", 0, offset) + 1
        line = text[line_start:offset]
        if "#define" in line:
            continue
        found.append((offset, match.group(1)))
    return found


def doc_kind(text: str, offset: int) -> str:
    """Return "doxygen", "comment" or "none" for the declaration at offset."""
    start = declaration_start(text, offset)
    before = text[:start].rstrip()
    if not before.endswith("*/"):
        return "none"
    comment_start = before.rfind("/*")
    if comment_start < 0:
        return "none"
    if before[comment_start:comment_start + 3] in ("/*!", "/**"):
        return "doxygen"
    return "comment"


def scan_header(path: Path) -> dict:
    text = path.read_text(encoding="utf-8", errors="replace")
    seen: set[str] = set()
    undocumented: list[str] = []
    documented = 0
    doxygen = 0
    for offset, name in declaration_entries(text):
        if name in seen:
            continue
        seen.add(name)
        kind = doc_kind(text, offset)
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
