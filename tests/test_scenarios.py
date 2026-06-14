"""Tests for scenario loading and tourist profile spawning."""

from __future__ import annotations

from pathlib import Path

import pytest

from src.models import Tourist
from src.scenarios import get_scenario, list_scenarios, load_scenarios
from src.simulation.population import spawn_tourists

ROOT = Path(__file__).resolve().parents[1]


def test_list_scenarios_includes_baseline():
    names = [n for n, _ in list_scenarios()]
    assert "baseline" in names
    assert "crowd_averse" in names
    assert "overtourism_peak" in names


def test_get_scenario_merges_overrides():
    cfg = get_scenario("budget_backpacker")
    assert cfg["scenario_name"] == "budget_backpacker"
    assert cfg["simulation"]["max_price_eur"] == 8.0
    assert cfg["simulation"]["num_tourists"] == 3000


def test_get_scenario_overtourism_peak():
    cfg = get_scenario("overtourism_peak")
    assert cfg["simulation"]["num_tourists"] == 8000
    assert cfg["simulation"]["num_days"] == 7
    assert cfg["crowding"]["initial_load_boost"] == pytest.approx(0.35)


def test_get_scenario_unknown_raises():
    with pytest.raises(KeyError, match="Unknown scenario"):
        get_scenario("nonexistent_scenario")


def test_tourist_default_profile_fields():
    t = Tourist(
        tourist_id="t0",
        interest_tags=frozenset({"museum"}),
        max_price_eur=20.0,
        travel_budget_km=5.0,
        lat=41.39,
        lon=2.17,
    )
    assert t.crowd_aversion == pytest.approx(0.3)
    assert t.sustainability_sensitivity == pytest.approx(0.5)
    assert t.prefers_outdoor is False
    assert t.travel_with_kids is False
    assert t.walking_tolerance == "medium"


def test_seminar_religious_fixed_profile():
    cfg = get_scenario("seminar_religious")
    tourists = spawn_tourists([], cfg, "seminar_religious", seed=42)
    assert len(tourists) == 1
    assert tourists[0].interest_tags == frozenset({"religious", "architecture", "history"})
    assert tourists[0].tourist_id == "case_study_01"


def test_crowd_averse_high_aversion():
    cfg = get_scenario("crowd_averse")
    # Minimal POI list for tag sampling
    from src.models import POI

    pois = [
        POI(
            poi_id="p1",
            name="Test POI",
            lat=41.39,
            lon=2.17,
            interest_tags=frozenset({"museum", "park"}),
        )
    ]
    tourists = spawn_tourists(pois, cfg, "crowd_averse", seed=99)
    mean_aversion = sum(t.crowd_aversion for t in tourists) / len(tourists)
    assert mean_aversion > 0.7


def test_load_scenarios_structure():
    scenarios = load_scenarios()
    assert "baseline" in scenarios
    assert "description" in scenarios["baseline"]
    assert "tourist_profile" in scenarios["baseline"]
