#!/usr/bin/env python3
"""Run the same steps as the GitHub Actions acceptance workflow locally.

The workflow (``.github/workflows/ci.yml``) checks out the pinned library
repositories from ``app/release-lock.json`` and runs the acceptance runner in
five shapes: Ubuntu/Windows x static/shared plus one sanitizer job. This script
mirrors that path so the CI configuration can be exercised on a developer
machine:

    python app/tools/ci_local.py                 # fetch the lock, static build
    python app/tools/ci_local.py --skip-fetch    # verify the current workspace
    python app/tools/ci_local.py --shared --jobs 8
    python app/tools/ci_local.py --all           # static + shared + sanitizer

``--all`` runs the three shapes the local platform can build; the sanitizer
shape adds ``--leak-check`` on Linux so the local mirror is at least as strict
as the workflow.
"""
from __future__ import annotations

import argparse
import os
import subprocess
import sys
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--workspace", type=Path,
                        default=Path(__file__).resolve().parents[2])
    parser.add_argument("--skip-fetch", action="store_true",
                        help="verify the current checkouts instead of cloning the lock")
    parser.add_argument("--shared", action="store_true")
    parser.add_argument("--all", action="store_true",
                        help="run static, shared and the sanitizer shape in turn")
    parser.add_argument("--jobs", type=int, default=4)
    parser.add_argument("--summary", type=Path)
    parser.add_argument("--dry-run", action="store_true",
                        help="print the commands without running them")
    args = parser.parse_args()
    workspace = args.workspace.resolve()
    app = workspace / "app"
    if not (app / "tools" / "run_acceptance.py").is_file():
        print(f"error: {app} does not look like the Quirewise app repository",
              file=sys.stderr)
        return 2
    fetch = [sys.executable, str(app / "tools" / "fetch_workspace.py"),
             "--workspace", str(workspace)]
    if args.skip_fetch:
        fetch.append("--verify-only")
    print("+ " + " ".join(fetch), flush=True)
    if not args.dry_run and subprocess.run(fetch).returncode != 0:
        return 1

    def run_shape(name: str, extra: list[str]) -> int:
        summary = (args.summary if args.summary and not args.all
                   else workspace / ".tmp" / f"ci-local-{name}-summary.json")
        command = [sys.executable, str(app / "tools" / "run_acceptance.py"),
                   "--workspace", str(workspace), "--jobs", str(args.jobs),
                   "--summary", str(summary), *extra]
        print("+ " + " ".join(command), flush=True)
        if args.dry_run:
            return 0
        return subprocess.run(command).returncode

    if not args.all:
        extra = ["--shared"] if args.shared else []
        return run_shape("shared" if args.shared else "static", extra)

    shapes: list[tuple[str, list[str]]] = [
        ("static", []),
        ("shared", ["--shared"]),
    ]
    if os.name != "nt":
        shapes.append(("sanitize", ["--sanitize", "--leak-check"]))
    failures = []
    for name, extra in shapes:
        if run_shape(name, extra) != 0:
            failures.append(name)
    if failures:
        print("failed shapes: " + ", ".join(failures), file=sys.stderr)
        return 1
    print(f"all {len(shapes)} local CI shapes passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
