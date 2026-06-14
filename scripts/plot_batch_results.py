#!/usr/bin/env python3
"""Bar charts from batch_results.csv for the written report (Figure: strategy comparison)."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.config import load_config  # noqa: E402

STRATEGY_ORDER = ["popularity", "interest_based", "sustainability"]
STRATEGY_LABELS = {
    "popularity": "Popularity",
    "interest_based": "Interest-based",
    "sustainability": "Sustainability",
}
STRATEGY_COLORS = {
    "popularity": "#f59e0b",
    "interest_based": "#34d399",
    "sustainability": "#38bdf8",
}

PANELS = [
    ("gini", "Gini coefficient (lower = more even)", False),
    ("hotspot_pct", "Hotspot visit share (lower = less overtourism)", True),
    ("entropy", "Visit entropy (higher = more dispersed)", False),
]


def load_summary(input_path: Path, scenario: str) -> pd.DataFrame:
    df = pd.read_csv(input_path)
    if scenario:
        filtered = df[df["scenario"] == scenario]
        if filtered.empty:
            available = sorted(df["scenario"].unique())
            msg = f"No rows for scenario={scenario!r} in {input_path}."
            if available:
                msg += f" Available scenarios: {', '.join(available)}."
            msg += f" Re-run: python scripts/run_batch.py --scenario {scenario}"
            raise ValueError(msg)
        df = filtered

    metrics = [m for m, _, _ in PANELS]
    grouped = df.groupby("strategy")[metrics].agg(["mean", "std"])
    rows = []
    for strategy in STRATEGY_ORDER:
        if strategy not in grouped.index:
            continue
        row = {"strategy": strategy, "label": STRATEGY_LABELS[strategy]}
        for metric, _, _ in PANELS:
            row[f"{metric}_mean"] = grouped.loc[strategy, (metric, "mean")]
            row[f"{metric}_std"] = grouped.loc[strategy, (metric, "std")]
        rows.append(row)
    return pd.DataFrame(rows)


def plot_summary(summary: pd.DataFrame, scenario: str, output: Path) -> None:
    fig, axes = plt.subplots(
        1,
        len(PANELS),
        figsize=(11.2, 4.1),
        constrained_layout=False,
    )
    if len(PANELS) == 1:
        axes = [axes]

    labels = summary["label"].tolist()
    x = range(len(labels))

    for ax, (metric, title, as_pct) in zip(axes, PANELS):
        means = summary[f"{metric}_mean"].tolist()
        stds = summary[f"{metric}_std"].tolist()
        colors = [STRATEGY_COLORS[s] for s in summary["strategy"]]

        if as_pct:
            means = [m * 100 for m in means]
            stds = [s * 100 for s in stds]
            ylabel = "Share of visits (%)"
        else:
            ylabel = "Value"

        ax.bar(
            x,
            means,
            yerr=stds,
            capsize=4,
            color=colors,
            edgecolor="#334155",
            linewidth=0.8,
        )
        ax.set_xticks(list(x), labels, rotation=15, ha="right")
        ax.set_title(title, fontsize=10, pad=12)
        ax.set_ylabel(ylabel, fontsize=9)
        ax.grid(axis="y", linestyle="--", alpha=0.35)
        ax.set_axisbelow(True)

    fig.suptitle(
        f"Recommender strategy comparison ({scenario} scenario, mean ± std, 4 seeds)",
        fontsize=12,
        y=0.97,
    )

    # Leave enough room between the main title and the subplot titles.
    fig.subplots_adjust(
        top=0.76,
        bottom=0.22,
        left=0.06,
        right=0.99,
        wspace=0.28,
    )

    output.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(output, dpi=200, bbox_inches="tight", facecolor="white")
    pdf_path = output.with_suffix(".pdf")
    fig.savefig(pdf_path, bbox_inches="tight", facecolor="white")
    plt.close(fig)


def write_report_figure(
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

    summary = load_summary(batch_path, scenario)
    report_dir = Path(cfg["paths"]["report_dir"])
    if not report_dir.is_absolute():
        report_dir = ROOT / report_dir
    out_path = Path(output_path) if output_path else report_dir / scenario / "figure.png"
    if not out_path.is_absolute():
        out_path = ROOT / out_path
    plot_summary(summary, scenario, out_path)

    if verbose:
        print(f"Wrote {out_path}")
        print(f"Wrote {out_path.with_suffix('.pdf')}")
    return out_path


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Plot batch_results.csv as report bar charts"
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
        help="Output PNG path (default: report/<scenario>/figure.png; PDF alongside)",
    )
    args = parser.parse_args()

    cfg = load_config()
    input_path = Path(args.input or cfg["paths"]["batch_results"])
    if not input_path.is_absolute():
        input_path = ROOT / input_path

    try:
        write_report_figure(
            args.scenario,
            input_path=input_path,
            output_path=Path(args.output) if args.output else None,
            cfg=cfg,
        )
    except (FileNotFoundError, ValueError) as exc:
        print(str(exc), file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
