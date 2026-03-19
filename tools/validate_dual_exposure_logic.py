#!/usr/bin/env python3

from __future__ import annotations

import argparse
import json
import os
import sys
from dataclasses import asdict
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
os.environ.setdefault("MPLCONFIGDIR", str(REPO_ROOT / ".mplconfig"))
(REPO_ROOT / ".mplconfig").mkdir(exist_ok=True)
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from core.mock_validation import print_results, run_checks


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate the key dual-exposure stereo logic on synthetic mock scenes."
    )
    parser.add_argument(
        "--json",
        type=Path,
        default=None,
        help="Optional path to write the raw validation results as JSON.",
    )
    args = parser.parse_args()

    results = run_checks()
    print_results(results)

    if args.json is not None:
        args.json.parent.mkdir(parents=True, exist_ok=True)
        args.json.write_text(json.dumps([asdict(result) for result in results], indent=2))

    return 0 if all(result.passed for result in results) else 1


if __name__ == "__main__":
    raise SystemExit(main())
