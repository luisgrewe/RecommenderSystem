#!/usr/bin/env python3
"""Batch ABM runs: 3 strategies × seeds, comparison table + CSV export.

This script runs one simulation scenario across all recommender strategies and
configured random seeds. For each run, it stores city-level distribution metrics
and an average profile consistency score computed across the tourist population.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Any

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.data.pipeline import load_processed_pois  # noqa: E402
from src.metrics.crowding import (  # noqa: E402
    gini_coefficient,
    hotspot_visit_pct,
    local_economic_impact,
    visit_entropy,
)
from src.metrics.recommendation_quality import profile_consistency  # noqa: E402
from src.recommenders.registry import get_strategy  # noqa: E402
from src.scenarios import get_scenario  # noqa: E402
from src.simulation.model import TourismModel  # noqa: E402
from src.simulation.population import spawn_tourists  # noqa: E402

HOTSPOT_SUBSTRINGS = [
    "Sagrada Família",
    "Casa Batlló",
    "Park Güell",
    "Boqueria",
    "Museu Picasso",
]


def average_profile_consistency(
    strategy: Any,
    tourists: list,
    pois: list,
    crowding: dict,
    top_k: int,
) -> float:
    """Average recommendation relevance across all tourists.

    For each tourist, the selected recommender generates a top-k list using the
    final crowding state of the simulation. The profile consistency metric then
    checks what fraction of those recommendations share at least one tag with
    the tourist's interests. The returned value is the population average.
    """
    if not tourists:
        return 0.0

    scores = []
    for tourist in tourists:
        recs = strategy.recommend(tourist, pois, crowding, top_k=top_k)
        scores.append(profile_consistency(recs, tourist))

    return sum(scores) / len(scores)


def run_single(pois, cfg: dict, strategy_name: str, seed: int) -> dict:
    strategy = get_strategy(strategy_name)
    tourists = spawn_tourists(pois, cfg, cfg.get("scenario_name"), seed)
    crowding_cfg = cfg["crowding"]
    sim_cfg = cfg["simulation"]
    top_k = cfg["recommenders"]["top_k"]

    model = TourismModel(
        pois=pois,
        tourists=tourists,
        strategy=strategy,
        num_days=sim_cfg["num_days"],
        daily_pois_per_tourist=sim_cfg["daily_pois_per_tourist"],
        soft_threshold=crowding_cfg["soft_threshold"],
        accept_steepness=crowding_cfg["accept_steepness"],
        decay_rate=crowding_cfg["decay_rate"],
        top_k=top_k,
        seed=seed,
        initial_load_boost=crowding_cfg.get("initial_load_boost", 0.0),
    )
    results = model.run()

    visit_values = list(results["total_visits"].values())
    poi_names = {p.poi_id: p.name for p in pois}
    poi_prices = {p.poi_id: p.price_eur for p in pois}

    return {
        "scenario": cfg.get("scenario_name", "baseline"),
        "strategy": strategy_name,
        "seed": seed,
        "total_visits": sum(visit_values),
        "gini": gini_coefficient(visit_values),
        "entropy": visit_entropy(visit_values),
        "hotspot_pct": hotspot_visit_pct(
            results["total_visits"],
            poi_names,
            HOTSPOT_SUBSTRINGS,
        ),
        "economic_impact": local_economic_impact(results["total_visits"], poi_prices),
        "profile_consistency": average_profile_consistency(
            strategy,
            tourists,
            pois,
            model.crowding,
            top_k=top_k,
        ),
    }


def run_scenario_batch(
    scenario_name: str,
    pois=None,
    *,
    verbose: bool = True,
) -> pd.DataFrame:
    cfg = get_scenario(scenario_name)
    if pois is None:
        pois = load_processed_pois(cfg["paths"]["processed_pois"])
    strategies = cfg["recommenders"]["strategies"]
    seeds = cfg["batch"]["seeds"]

    if verbose:
        print(f"Scenario: {cfg['scenario_name']} — {cfg.get('scenario_description', '')}")

    rows = []
    for strategy in strategies:
        for seed in seeds:
            if verbose:
                print(f"Running {strategy} seed={seed}...", flush=True)
            rows.append(run_single(pois, cfg, strategy, seed))

    return pd.DataFrame(rows)


def save_scenario_batch(df: pd.DataFrame, scenario_name: str, out_path: Path) -> None:
    if not out_path.is_absolute():
        out_path = ROOT / out_path
    out_path.parent.mkdir(parents=True, exist_ok=True)

    if out_path.exists():
        existing = pd.read_csv(out_path)
        existing = existing[existing["scenario"] != scenario_name]
        df = pd.concat([existing, df], ignore_index=True)

    df.to_csv(out_path, index=False)


def main() -> None:
    parser = argparse.ArgumentParser(description="Run batch ABM evaluation")
    parser.add_argument(
        "--scenario",
        default="baseline",
        help="Scenario preset from config/scenarios.yaml (default: baseline)",
    )
    args = parser.parse_args()

    cfg = get_scenario(args.scenario)
    out_path = Path(cfg["paths"]["batch_results"])

    df = run_scenario_batch(args.scenario)
    save_scenario_batch(df, cfg["scenario_name"], out_path)

    summary = df.groupby("strategy").mean(numeric_only=True)
    print("\n" + "=" * 72)
    print(f"Batch comparison — scenario={cfg['scenario_name']} (mean over seeds)")
    print("=" * 72)
    print(summary.round(4).to_string())
    print(f"\nSaved: {out_path if out_path.is_absolute() else ROOT / out_path}")


if __name__ == "__main__":
    main()