#!/usr/bin/env python3
"""Aggregate batch_results.csv into report Table 3 (mean ± std by strategy)."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.config import load_config  # noqa: E402

METRICS = [
    "gini",
    "hotspot_pct",
    "entropy",
    "total_visits",
    "economic_impact",
    "profile_consistency",
]

STRATEGY_LABELS = {
    "popularity": "Popularity-based",
    "interest_based": "Interest-based",
    "sustainability": "Sustainability-aware",
}

STRATEGY_ORDER = ["popularity", "interest_based", "sustainability"]


def summarize(df: pd.DataFrame) -> pd.DataFrame:
    grouped = df.groupby("strategy")[METRICS].agg(["mean", "std"])
    flat = grouped.copy()
    flat.columns = [f"{metric}_{stat}" for metric, stat in flat.columns]
    flat = flat.reset_index()
    flat["strategy_label"] = flat["strategy"].map(
        lambda s: STRATEGY_LABELS.get(s, s)
    )
    order = {s: i for i, s in enumerate(STRATEGY_ORDER)}
    flat["_order"] = flat["strategy"].map(lambda s: order.get(s, 99))
    return flat.sort_values("_order").drop(columns="_order").reset_index(drop=True)


def _pm(mean: float, std: float, decimals: int = 3) -> str:
    return f"{mean:.{decimals}f} ± {std:.{decimals}f}"


def build_display_table(summary: pd.DataFrame) -> pd.DataFrame:
    rows: list[dict[str, str]] = []
    for _, row in summary.iterrows():
        rows.append(
            {
                "Strategy": row["strategy_label"],
                "Gini ↓": _pm(row["gini_mean"], row["gini_std"]),
                "Hotspot share ↓": _pm(row["hotspot_pct_mean"], row["hotspot_pct_std"]),
                "Visit entropy ↑": _pm(row["entropy_mean"], row["entropy_std"]),
                "Total visits": _pm(
                    row["total_visits_mean"], row["total_visits_std"], decimals=0
                ),
                "Profile consistency ↑": _pm(
                    row["profile_consistency_mean"],
                    row["profile_consistency_std"],
                ),
            }
        )
    return pd.DataFrame(rows)


def print_markdown(display: pd.DataFrame, scenario: str) -> None:
    print(f"\nTable 3 — scenario: {scenario}\n")
    header = "| " + " | ".join(display.columns) + " |"
    sep = "| " + " | ".join(["---"] * len(display.columns)) + " |"
    print(header)
    print(sep)
    for _, row in display.iterrows():
        print("| " + " | ".join(str(row[c]) for c in display.columns) + " |")
    print()


def write_report_table(
    scenario: str,
    *,
    input_path: Path | None = None,
    output_path: Path | None = None,
    cfg: dict | None = None,
    verbose: bool = True,
) -> Path:
    cfg = cfg or load_config()
    batch_path = Path(input_path or cfg["paths"]["batch_results"])
    if not batch_path.is_absolute():
        batch_path = ROOT / batch_path

    if not batch_path.exists():
        raise FileNotFoundError(
            f"Missing {batch_path}. Run: python scripts/run_batch.py --scenario {scenario}"
        )

    df = pd.read_csv(batch_path)
    filtered = df[df["scenario"] == scenario]
    if filtered.empty:
        available = sorted(df["scenario"].unique())
        msg = f"No rows for scenario={scenario!r} in {batch_path}."
        if available:
            msg += f" Available scenarios: {', '.join(available)}."
        raise ValueError(msg)

    summary = summarize(filtered)
    display = build_display_table(summary)

    report_dir = Path(cfg["paths"]["report_dir"])
    if not report_dir.is_absolute():
        report_dir = ROOT / report_dir
    out_path = Path(output_path) if output_path else report_dir / scenario / "table3.csv"
    if not out_path.is_absolute():
        out_path = ROOT / out_path
    out_path.parent.mkdir(parents=True, exist_ok=True)
    display.to_csv(out_path, index=False)

    if verbose:
        print(f"Wrote {out_path}")
        print_markdown(display, scenario)
    return out_path


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Summarize batch_results.csv for report Table 3"
    )
    parser.add_argument(
        "--input",
        default=None,
        help="Raw batch CSV (default: paths.batch_results from config)",
    )
    parser.add_argument(
        "--scenario",
        default="baseline",
        help="Scenario name to filter (default: baseline)",
    )
    parser.add_argument(
        "--output",
        default=None,
        help="Report table CSV (default: report/<scenario>/table3.csv)",
    )
    args = parser.parse_args()

    cfg = load_config()
    input_path = Path(args.input or cfg["paths"]["batch_results"])
    if not input_path.is_absolute():
        input_path = ROOT / input_path

    try:
        write_report_table(
            args.scenario,
            input_path=input_path,
            output_path=Path(args.output) if args.output else None,
            cfg=cfg,
        )
    except (FileNotFoundError, ValueError) as exc:
        print(str(exc), file=sys.stderr)
        if isinstance(exc, ValueError):
            print(
                f"Re-run: python scripts/run_batch.py --scenario {args.scenario}",
                file=sys.stderr,
            )
        sys.exit(1)


if __name__ == "__main__":
    main()
