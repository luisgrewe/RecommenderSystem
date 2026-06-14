"""Tests for recommender strategies."""

from pathlib import Path

import pytest

from src.data.pipeline import load_processed_pois, run_pipeline
from src.models import CrowdingState, Tourist
from src.recommenders.registry import STRATEGIES

ROOT = Path(__file__).resolve().parents[1]
PROCESSED = ROOT / "data" / "processed" / "pois_simulation.csv"


@pytest.fixture(scope="module")
def pois():
    if not PROCESSED.exists():
        run_pipeline()
    return load_processed_pois(PROCESSED)


@pytest.fixture
def religious_tourist():
    return Tourist(
        tourist_id="test_01",
        interest_tags=frozenset({"religious", "architecture"}),
        max_price_eur=35.0,
        travel_budget_km=8.0,
        lat=41.387,
        lon=2.173,
    )


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


def test_sustainability_differs_from_popularity(pois, religious_tourist, crowding):
    pop = STRATEGIES["popularity"].recommend(religious_tourist, pois, crowding, top_k=5)
    sus = STRATEGIES["sustainability"].recommend(religious_tourist, pois, crowding, top_k=5)
    pop_ids = [r.poi.poi_id for r in pop]
    sus_ids = [r.poi.poi_id for r in sus]
    assert pop_ids != sus_ids or pop[0].score != sus[0].score


def test_sustainability_has_breakdown(pois, religious_tourist, crowding):
    sus = STRATEGIES["sustainability"].recommend(religious_tourist, pois, crowding, top_k=3)
    assert all(r.breakdown is not None for r in sus)
    assert sus[0].breakdown.total == pytest.approx(sus[0].score, rel=1e-6)
