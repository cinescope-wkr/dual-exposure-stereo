#!/usr/bin/env python3

from __future__ import annotations

import argparse
import json
from pathlib import Path

from paper_benchmarks import add_shared_args, evaluate_method, print_results, save_results


SUPPORTED_ABLATIONS = (
    ("full_model", {}),
    ("without_adec", {"disable_adec": True}),
    ("without_weighted_fusion", {"disable_weighted_fusion": True}),
    ("without_motion_compensation", {"disable_motion_compensation": True}),
)

UNSUPPORTED_PAPER_ROWS = (
    "Backbone [51] comparisons are not packaged in this repository.",
    "Exposure-level fusion rows are not implemented as separate code paths in this repository.",
    "Disparity-level fusion rows are not implemented as separate code paths in this repository.",
)


def main() -> int:
    parser = argparse.ArgumentParser(description="Run the directly supported Table 2 ADEC ablations on the synthetic benchmark.")
    parser.add_argument("--output_json", type=str, default=None)
    add_shared_args(parser)
    args = parser.parse_args()

    rows = []
    for ablation_name, flags in SUPPORTED_ABLATIONS:
        run_args = argparse.Namespace(**vars(args))
        for key, value in flags.items():
            setattr(run_args, key, value)
        row = evaluate_method(run_args, "adec", "synthetic")
        row["ablation_name"] = ablation_name
        rows.append(row)

    print_results(rows)
    print("\nUnsupported Table 2 rows:")
    for item in UNSUPPORTED_PAPER_ROWS:
        print(f"- {item}")

    save_results(rows, args.output_json)
    if args.output_json is not None:
        output_file = Path(args.output_json)
        unsupported_file = output_file.with_name(output_file.stem + "_unsupported.json")
        unsupported_file.write_text(json.dumps(list(UNSUPPORTED_PAPER_ROWS), indent=2))

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
