"""Tests for trip pace and group type effects."""

from src.models import CrowdingState, POI, Tourist
from src.recommenders.interest_based import InterestBasedRecommender
from src.recommenders.trip_profile import (
    accept_steepness_for,
    effective_crowd_aversion,
    group_type_score_adjustment,
)
from src.simulation.visit_logic import accept_probability


def _park() -> POI:
    return POI(
        "park1",
        "Parc Test",
        41.39,
        2.17,
        price_eur=0.0,
        interest_tags=frozenset({"park", "nature"}),
        popularity_score=0.4,
    )


def _museum() -> POI:
    return POI(
        "mus1",
        "Museum Test",
        41.39,
        2.17,
        price_eur=15.0,
        interest_tags=frozenset({"museum"}),
        popularity_score=0.7,
    )


def test_family_boosts_park_over_museum_score():
    family = Tourist(
        tourist_id="f",
        interest_tags=frozenset({"museum", "park"}),
        max_price_eur=30.0,
        travel_budget_km=8.0,
        lat=41.387,
        lon=2.173,
        group_type="family",
    )
    solo = Tourist(
        tourist_id="s",
        interest_tags=family.interest_tags,
        max_price_eur=30.0,
        travel_budget_km=8.0,
        lat=41.387,
        lon=2.173,
        group_type="solo",
    )
    assert group_type_score_adjustment(family, _park()) > group_type_score_adjustment(
        solo, _park()
    )
    assert group_type_score_adjustment(family, _museum()) < group_type_score_adjustment(
        solo, _museum()
    )


def test_relaxed_increases_effective_crowd_aversion():
    relaxed = Tourist(
        tourist_id="r",
        interest_tags=frozenset({"park"}),
        max_price_eur=30.0,
        travel_budget_km=8.0,
        lat=41.387,
        lon=2.173,
        trip_pace="relaxed",
        crowd_aversion=0.3,
    )
    packed = Tourist(
        tourist_id="p",
        interest_tags=frozenset({"park"}),
        max_price_eur=30.0,
        travel_budget_km=8.0,
        lat=41.387,
        lon=2.173,
        trip_pace="packed",
        crowd_aversion=0.3,
    )
    assert effective_crowd_aversion(relaxed) > effective_crowd_aversion(packed)


def test_pace_changes_accept_probability():
    tourist_relaxed = Tourist(
        tourist_id="r",
        interest_tags=frozenset({"park"}),
        max_price_eur=30.0,
        travel_budget_km=8.0,
        lat=41.387,
        lon=2.173,
        trip_pace="relaxed",
    )
    tourist_packed = Tourist(
        tourist_id="p",
        interest_tags=frozenset({"park"}),
        max_price_eur=30.0,
        travel_budget_km=8.0,
        lat=41.387,
        lon=2.173,
        trip_pace="packed",
    )
    state = CrowdingState(poi_id="x", capacity=500, baseline_intensity=0.55, visits_today=300)

    relaxed_prob = accept_probability(
        0.6,
        state,
        crowd_aversion=effective_crowd_aversion(tourist_relaxed),
        steepness=accept_steepness_for(tourist_relaxed, 5.0),
    )
    packed_prob = accept_probability(
        0.6,
        state,
        crowd_aversion=effective_crowd_aversion(tourist_packed),
        steepness=accept_steepness_for(tourist_packed, 5.0),
    )
    assert packed_prob > relaxed_prob


def test_pace_reorders_interest_based_recommendations():
    """Relaxed prefers nearby/quiet; packed prefers famous even if busier."""
    nearby_quiet = POI(
        "near",
        "Quiet Chapel",
        41.388,
        2.174,
        price_eur=0.0,
        interest_tags=frozenset({"religious"}),
        popularity_score=0.35,
        baseline_tourism_intensity=0.15,
    )
    far_famous = POI(
        "far",
        "Famous Basilica",
        41.42,
        2.20,
        price_eur=12.0,
        interest_tags=frozenset({"religious"}),
        popularity_score=0.85,
        baseline_tourism_intensity=0.80,
    )
    pois = [nearby_quiet, far_famous]
    crowding = {
        p.poi_id: CrowdingState(
            poi_id=p.poi_id,
            capacity=p.capacity,
            baseline_intensity=p.baseline_tourism_intensity,
            visits_today=200 if p.poi_id == "far" else 20,
        )
        for p in pois
    }
    base = dict(
        interest_tags=frozenset({"religious"}),
        max_price_eur=50.0,
        travel_budget_km=8.0,
        lat=41.387,
        lon=2.173,
        crowd_aversion=0.3,
    )
    relaxed = Tourist(tourist_id="r", trip_pace="relaxed", **base)
    packed = Tourist(tourist_id="p", trip_pace="packed", **base)
    rec = InterestBasedRecommender()
    assert rec.recommend(relaxed, pois, crowding, top_k=1)[0].poi.poi_id == "near"
    assert rec.recommend(packed, pois, crowding, top_k=1)[0].poi.poi_id == "far"


def test_family_reorders_interest_based_recommendations():
    pois = [_park(), _museum()]
    crowding = {
        p.poi_id: CrowdingState(
            poi_id=p.poi_id,
            capacity=p.capacity,
            baseline_intensity=p.baseline_tourism_intensity,
        )
        for p in pois
    }
    family = Tourist(
        tourist_id="f",
        interest_tags=frozenset({"museum", "park"}),
        max_price_eur=30.0,
        travel_budget_km=8.0,
        lat=41.387,
        lon=2.173,
        group_type="family",
    )
    solo = Tourist(
        tourist_id="s",
        interest_tags=frozenset({"museum", "park"}),
        max_price_eur=30.0,
        travel_budget_km=8.0,
        lat=41.387,
        lon=2.173,
        group_type="solo",
    )
    rec = InterestBasedRecommender()
    family_top = rec.recommend(family, pois, crowding, top_k=1)[0].poi.poi_id
    solo_top = rec.recommend(solo, pois, crowding, top_k=1)[0].poi.poi_id
    assert family_top == "park1"
    assert solo_top == "mus1"
