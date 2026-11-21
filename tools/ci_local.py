#!/usr/bin/env python3
"""Run the same steps as the GitHub Actions acceptance workflow locally.

The workflow (``.github/workflows/ci.yml``) checks out the pinned library
repositories from ``app/release-lock.json`` and runs the acceptance runner.
This script mirrors that path so the CI configuration can be exercised on a
developer machine:

    python app/tools/ci_local.py                 # fetch the lock, static build
    python app/tools/ci_local.py --skip-fetch    # verify the current workspace
    python app/tools/ci_local.py --shared --jobs 8
"""
from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--workspace", type=Path,
                        default=Path(__file__).resolve().parents[2])
    parser.add_argument("--skip-fetch", action="store_true",
                        help="verify the current checkouts instead of cloning the lock")
    parser.add_argument("--shared", action="store_true")
    parser.add_argument("--jobs", type=int, default=4)
    parser.add_argument("--summary", type=Path)
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
    if subprocess.run(fetch).returncode != 0:
        return 1
    summary = args.summary or workspace / ".tmp" / "ci-local-summary.json"
    command = [sys.executable, str(app / "tools" / "run_acceptance.py"),
               "--workspace", str(workspace), "--jobs", str(args.jobs),
               "--summary", str(summary)]
    if args.shared:
        command.append("--shared")
    print("+ " + " ".join(command))
    return subprocess.run(command).returncode


if __name__ == "__main__":
    sys.exit(main())
