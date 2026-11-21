#!/usr/bin/env python3
"""Mutate sample PDFs and fail on any sanitizer diagnostic or crash.

The acceptance matrices already run the checked-in fixtures, but a parser that
only ever sees well-formed input hides its robustness. This harness flips random
bytes in a handful of real fixtures, runs the text route under an instrumented
build, and reports every crash or sanitizer report together with the mutated
input so it can be replayed:

    python app/tools/fuzz_pdf.py --binary .tmp/acceptance/linux-static-asan/app/quirewise \
        --iterations 500 --seed 20261121

Exit code 0 means every mutated case either converted or was rejected with a
normal error status.
"""
from __future__ import annotations

import argparse
import os
import random
import subprocess
import sys
import tempfile
from pathlib import Path

SAMPLES = [
    "libraries/quirewise-document/tests/data/columns3.pdf",
    "libraries/quirewise-document/tests/data/table_gaps.pdf",
    "libraries/quirewise-document/tests/data/merge_objstm.pdf",
    "app/testfile/pdf/basic/lorem-ipsum.pdf",
]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--workspace", type=Path,
                        default=Path(__file__).resolve().parents[2])
    parser.add_argument("--binary", type=Path, required=True,
                        help="quirewise executable to exercise")
    parser.add_argument("--iterations", type=int, default=200)
    parser.add_argument("--seed", type=int, default=20261121)
    parser.add_argument("--keep", type=Path,
                        help="directory for saved crashes (default: .tmp)")
    args = parser.parse_args()

    workspace = args.workspace.resolve()
    binary = args.binary if args.binary.is_absolute() else workspace / args.binary
    if not binary.is_file():
        print(f"error: missing binary {binary}", file=sys.stderr)
        return 2
    samples = [workspace / name for name in SAMPLES if (workspace / name).is_file()]
    if not samples:
        print("error: no sample PDFs found", file=sys.stderr)
        return 2
    keep = (args.keep or workspace / ".tmp").resolve()
    keep.mkdir(parents=True, exist_ok=True)
    random.seed(args.seed)

    env = os.environ.copy()
    env["ASAN_OPTIONS"] = "detect_leaks=0:abort_on_error=1"
    env["UBSAN_OPTIONS"] = "halt_on_error=1:print_stacktrace=1"

    crashes = 0
    with tempfile.TemporaryDirectory() as tmp:
        for index in range(args.iterations):
            sample = random.choice(samples)
            data = bytearray(sample.read_bytes())
            for _ in range(random.randint(1, 6)):
                position = random.randrange(len(data))
                data[position] = random.randrange(256)
            source = Path(tmp) / f"case{index}.pdf"
            source.write_bytes(bytes(data))
            target = Path(tmp) / f"out{index}.txt"
            result = subprocess.run([str(binary), str(source), "--to", "txt",
                                     "-o", str(target)], capture_output=True,
                                    text=True, env=env, timeout=60)
            stderr = result.stderr
            bad = ("AddressSanitizer" in stderr or "runtime error" in stderr
                   or result.returncode not in (0, 1))
            if bad:
                crashes += 1
                saved = keep / f"fuzz-crash-{args.seed}-{index}.pdf"
                saved.write_bytes(bytes(data))
                print(f"crash {index}: rc={result.returncode} "
                      f"sample={sample.name} saved={saved}")
                if stderr:
                    print(stderr.splitlines()[-1])
    print(f"{args.iterations} cases, {crashes} crashes")
    return 1 if crashes else 0


if __name__ == "__main__":
    sys.exit(main())
