#!/usr/bin/env python3
"""List scenarios or compare batch results across all scenario presets."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))

from src.data.pipeline import load_processed_pois  # noqa: E402
from src.scenarios import get_scenario, list_scenarios  # noqa: E402
from run_batch import run_single  # noqa: E402


def _print_scenario_list() -> None:
    print("Available scenarios:")
    print("-" * 72)
    for name, description in list_scenarios():
        print(f"  {name:22s}  {description}")


def _compare_all() -> None:
    pois = load_processed_pois(get_scenario("baseline")["paths"]["processed_pois"])
    rows = []

    for name, description in list_scenarios():
        cfg = get_scenario(name)
        strategies = cfg["recommenders"]["strategies"]
        seeds = cfg["batch"]["seeds"]
        print(f"\n=== {name}: {description} ===")
        for strategy in strategies:
            for seed in seeds:
                print(f"  {strategy} seed={seed}...", flush=True)
                row = run_single(pois, cfg, strategy, seed)
                rows.append(row)

    df = pd.DataFrame(rows)
    summary = (
        df.groupby(["scenario", "strategy"])
        .mean(numeric_only=True)
        .round(4)
    )
    print("\n" + "=" * 72)
    print("Cross-scenario comparison (mean over seeds)")
    print("=" * 72)
    print(summary.to_string())


def main() -> None:
    parser = argparse.ArgumentParser(description="Scenario management and comparison")
    parser.add_argument("--list", action="store_true", help="List all scenario presets")
    parser.add_argument(
        "--compare",
        action="store_true",
        help="Run batch across all scenarios and print summary table",
    )
    args = parser.parse_args()

    if args.list:
        _print_scenario_list()
        return

    if args.compare:
        _compare_all()
        return

    parser.print_help()


if __name__ == "__main__":
    main()
