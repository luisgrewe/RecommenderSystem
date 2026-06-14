"""Tests for personalised recommendation insights."""

from pathlib import Path

import pytest

from src.data.pipeline import load_processed_pois, run_pipeline
from src.models import CrowdingState, Tourist
from src.recommenders.filters import poi_exclusion_reason
from src.recommenders.registry import STRATEGIES
from src.viz.insights import build_recommendation_insights_for

ROOT = Path(__file__).resolve().parents[1]
PROCESSED = ROOT / "data" / "processed" / "pois_simulation.csv"


@pytest.fixture(scope="module")
def pois():
    if not PROCESSED.exists():
        run_pipeline()
    return load_processed_pois(PROCESSED)


@pytest.fixture
def crowding(pois):
    return {
        p.poi_id: CrowdingState(
            poi_id=p.poi_id,
            capacity=p.capacity,
            baseline_intensity=p.baseline_tourism_intensity,
        )
        for p in pois
    }


def test_limited_mobility_filters_far_pois(pois, crowding):
    tourist = Tourist(
        tourist_id="mobility",
        interest_tags=frozenset({"museum"}),
        max_price_eur=50.0,
        travel_budget_km=10.0,
        lat=41.387,
        lon=2.173,
        walking_tolerance="low",
    )
    far_poi = max(
        pois,
        key=lambda p: abs(p.lat - tourist.lat) + abs(p.lon - tourist.lon),
    )
    reason = poi_exclusion_reason(tourist, far_poi, crowding)
    assert reason is not None
    assert "mobility" in reason.lower() or "walk" in reason.lower()


def test_must_visit_pinned_even_when_over_budget(pois, crowding):
    expensive = max(pois, key=lambda p: p.price_eur or 0)
    tourist = Tourist(
        tourist_id="you",
        interest_tags=frozenset({"museum"}),
        max_price_eur=5.0,
        travel_budget_km=8.0,
        lat=41.387,
        lon=2.173,
    )
    insights = build_recommendation_insights_for(
        tourist,
        STRATEGIES["sustainability"],
        pois,
        crowding,
        top_k=5,
        must_visit_poi_ids=frozenset({expensive.poi_id}),
    )
    assert insights
    assert insights[0].poi_name == expensive.name
    assert insights[0].status == "blocked"
    assert insights[0].entry_price.startswith("€")
    assert insights[0].budget_limit == "€5"
