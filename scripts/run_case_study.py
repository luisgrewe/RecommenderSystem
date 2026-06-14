#!/usr/bin/env python3
"""Case study: religious-building tourist — compare recommenders side by side."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.data.pipeline import load_processed_pois  # noqa: E402
from src.models import CrowdingState  # noqa: E402
from src.recommenders.registry import STRATEGIES  # noqa: E402
from src.scenarios import get_scenario  # noqa: E402
from src.simulation.population import spawn_tourists  # noqa: E402


def main() -> None:
    parser = argparse.ArgumentParser(description="Run recommender case study")
    parser.add_argument(
        "--scenario",
        default="seminar_religious",
        help="Scenario preset (default: seminar_religious)",
    )
    args = parser.parse_args()

    cfg = get_scenario(args.scenario)
    pois = load_processed_pois(cfg["paths"]["processed_pois"])
    tourists = spawn_tourists(pois, cfg, args.scenario, seed=cfg["simulation"]["random_seed"])
    tourist = tourists[0]

    crowding = {
        p.poi_id: CrowdingState(
            poi_id=p.poi_id,
            capacity=p.capacity,
            baseline_intensity=p.baseline_tourism_intensity,
        )
        for p in pois
    }

    print("=" * 72)
    print(f"Case study — scenario: {cfg['scenario_name']}")
    print(f"Profile tags: {sorted(tourist.interest_tags)}")
    print(
        f"crowd_aversion={tourist.crowd_aversion:.2f}  "
        f"sustainability_sensitivity={tourist.sustainability_sensitivity:.2f}"
    )
    print("=" * 72)

    for name, strategy in STRATEGIES.items():
        recs = strategy.recommend(tourist, pois, crowding, top_k=5)
        print(f"\n--- {name} ---")
        for i, rec in enumerate(recs, 1):
            tags = ", ".join(sorted(rec.poi.interest_tags))
            line = f"  {i}. {rec.poi.name[:50]:50s} score={rec.score:.3f} tags=[{tags}]"
            print(line)
            if rec.breakdown:
                b = rec.breakdown
                print(
                    f"     breakdown: interest={b.interest:.2f} env={b.environment:.2f} "
                    f"culture={b.culture:.2f} economy={b.economy:.2f} "
                    f"crowd_disp={b.crowding_dispersion:.2f}"
                )


if __name__ == "__main__":
    main()
