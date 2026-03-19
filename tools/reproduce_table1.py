#!/usr/bin/env python3

from __future__ import annotations

import argparse

from paper_benchmarks import DEFAULT_DATASETS, DEFAULT_METHODS, add_shared_args, evaluate_method, print_results, save_results


def main() -> int:
    parser = argparse.ArgumentParser(description="Reproduce the Table 1 comparison rows that are supported by this repository.")
    parser.add_argument("--methods", nargs="+", choices=DEFAULT_METHODS, default=list(DEFAULT_METHODS))
    parser.add_argument("--datasets", nargs="+", choices=DEFAULT_DATASETS, default=list(DEFAULT_DATASETS))
    parser.add_argument("--output_json", type=str, default=None)
    add_shared_args(parser)
    args = parser.parse_args()

    rows = []
    for dataset in args.datasets:
        for method in args.methods:
            row = evaluate_method(args, method, dataset)
            rows.append(row)

    print_results(rows)
    save_results(rows, args.output_json)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
