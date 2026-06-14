#!/usr/bin/env python3
"""Run batch simulations and report outputs for all (or selected) scenarios."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))

from src.config import load_config  # noqa: E402
from src.data.pipeline import load_processed_pois  # noqa: E402
from src.scenarios import get_scenario, list_scenarios  # noqa: E402
from plot_batch_results import write_report_figure  # noqa: E402
from run_batch import run_scenario_batch, save_scenario_batch  # noqa: E402
from summarize_batch_results import write_report_table  # noqa: E402

# Single-tourist case study — use run_case_study.py instead of batch reports.
DEFAULT_EXCLUDE = {"seminar_religious"}


def resolve_scenarios(
    names: list[str] | None,
    *,
    exclude: set[str],
) -> list[str]:
    available = [name for name, _ in list_scenarios()]
    if names:
        unknown = sorted(set(names) - set(available))
        if unknown:
            raise ValueError(f"Unknown scenario(s): {', '.join(unknown)}")
        return names
    return [name for name in available if name not in exclude]


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Run batch + report table/figure for all scenarios"
    )
    parser.add_argument(
        "--scenarios",
        nargs="*",
        default=None,
        help="Subset of scenarios (default: all except seminar_religious)",
    )
    parser.add_argument(
        "--include-case-study",
        action="store_true",
        help="Also run seminar_religious (normally excluded)",
    )
    parser.add_argument(
        "--reports-only",
        action="store_true",
        help="Skip simulations; rebuild report/ from existing batch_results.csv",
    )
    parser.add_argument(
        "--batch-only",
        action="store_true",
        help="Run simulations only; skip report table and figure",
    )
    args = parser.parse_args()

    exclude = set() if args.include_case_study else DEFAULT_EXCLUDE
    try:
        scenarios = resolve_scenarios(args.scenarios, exclude=exclude)
    except ValueError as exc:
        print(str(exc), file=sys.stderr)
        sys.exit(1)

    cfg = load_config()
    batch_path = Path(cfg["paths"]["batch_results"])
    if not batch_path.is_absolute():
        batch_path = ROOT / batch_path

    print(f"Scenarios ({len(scenarios)}): {', '.join(scenarios)}\n")

    if not args.reports_only:
        pois = load_processed_pois(cfg["paths"]["processed_pois"])
        for i, scenario in enumerate(scenarios, start=1):
            print("=" * 72)
            print(f"[{i}/{len(scenarios)}] Batch — {scenario}")
            print("=" * 72)
            df = run_scenario_batch(scenario, pois=pois)
            save_scenario_batch(df, scenario, batch_path)
            summary = df.groupby("strategy").mean(numeric_only=True)
            print(summary.round(4).to_string())
            print(f"Updated: {batch_path}\n")

    if args.batch_only:
        print("Done (batch only).")
        return

    if not batch_path.exists():
        print(f"Missing {batch_path}. Re-run without --reports-only.", file=sys.stderr)
        sys.exit(1)

    report_dir = Path(cfg["paths"]["report_dir"])
    if not report_dir.is_absolute():
        report_dir = ROOT / report_dir

    for i, scenario in enumerate(scenarios, start=1):
        print("=" * 72)
        print(f"[{i}/{len(scenarios)}] Report — {scenario}")
        print("=" * 72)
        try:
            write_report_table(scenario, cfg=cfg)
            write_report_figure(scenario, cfg=cfg)
        except (FileNotFoundError, ValueError) as exc:
            print(f"Skipped {scenario}: {exc}", file=sys.stderr)
        print()

    print("Done.")
    print(f"Batch data: {batch_path}")
    print(f"Report outputs: {report_dir}/<scenario>/table3.csv, figure.png, figure.pdf")


if __name__ == "__main__":
    main()
