"""Human-readable recommender insights for the dashboard."""

from __future__ import annotations

from dataclasses import dataclass

from src.models import CrowdingState, POI, Recommendation, Tourist
from src.recommenders.base import RecommenderStrategy
from src.recommenders.filters import poi_exclusion_reason
from src.recommenders.registry import get_strategy
from src.recommenders.trip_profile import (
    accept_steepness_for,
    effective_crowd_aversion,
    trip_profile_reasons,
)
from src.simulation.geo import haversine_km
from src.simulation.visit_logic import accept_probability
from src.simulation.model import TourismModel
from src.viz.rec_format import ENTRY_FREE, entry_price_for_card, is_free_entry_poi


@dataclass(frozen=True)
class RecommendationInsight:
    rank: int
    poi_name: str
    score: float
    crowd_pct: float
    distance_km: float
    status: str  # recommended | caution | likely_skip | must_visit | blocked
    reasons: list[str]
    accept_pct: float
    entry_price: str = ""
    budget_limit: str = ""


@dataclass(frozen=True)
class CrowdedPOI:
    name: str
    crowd_pct: float
    visits_today: int
    district: str


def baseline_crowding(pois: list[POI]) -> dict[str, CrowdingState]:
    return {
        p.poi_id: CrowdingState(
            poi_id=p.poi_id,
            capacity=p.capacity,
            baseline_intensity=p.baseline_tourism_intensity,
        )
        for p in pois
    }


def _crowd_level(crowding: float) -> str:
    if crowding >= 0.65:
        return "high"
    if crowding >= 0.35:
        return "medium"
    return "low"


def _status_for(
    rec: Recommendation,
    tourist: Tourist,
    crowding: CrowdingState,
    *,
    soft_threshold: float,
    steepness: float,
    is_must_visit: bool = False,
) -> tuple[str, list[str], float]:
    reasons: list[str] = []
    crowd = crowding.combined_crowding
    level = _crowd_level(crowd)

    if is_must_visit:
        reasons.append("On your must-visit list")

    if crowd >= 0.65:
        reasons.append(f"High crowding ({crowd:.0%}) — hotspot under pressure")
    elif crowd >= 0.35:
        reasons.append(f"Moderate crowding ({crowd:.0%})")

    dist = haversine_km(tourist.lat, tourist.lon, rec.poi.lat, rec.poi.lon)
    if tourist.walking_tolerance == "low" and dist > 2.0:
        reasons.append(f"Long walk ({dist:.1f} km) — hard for limited mobility")
    elif dist > tourist.travel_budget_km * 0.8:
        reasons.append(f"Near travel limit ({dist:.1f} km)")

    if tourist.crowd_aversion >= 0.7 and crowd >= 0.45:
        reasons.append("Crowd-averse profile — may skip busy places")

    eff_aversion = effective_crowd_aversion(tourist)
    if eff_aversion > tourist.crowd_aversion + 0.05 and crowd >= 0.35:
        reasons.append("Trip profile — less tolerance for crowding today")

    for hint in trip_profile_reasons(tourist, rec.poi):
        if hint not in reasons:
            reasons.append(hint)

    if is_free_entry_poi(rec.poi):
        reasons.append(f"{ENTRY_FREE} — budget-friendly")
    elif rec.poi.price_eur and rec.poi.price_eur <= tourist.max_price_eur * 0.5:
        reasons.append("Affordable ticket")

    overlap = tourist.interest_tags & rec.poi.interest_tags
    if overlap:
        reasons.append(f"Matches interests: {', '.join(sorted(overlap))}")

    if rec.breakdown:
        b = rec.breakdown
        if b.environment >= 0.8:
            reasons.append("Low overtourism area (sustainable)")
        if b.culture >= 0.85:
            reasons.append("Supports local culture")
        if b.crowd_penalty > 0.05:
            reasons.append("Crowd penalty applied in score")

    accept = accept_probability(
        rec.score,
        crowding,
        soft_threshold=soft_threshold,
        steepness=accept_steepness_for(tourist, steepness),
        crowd_aversion=eff_aversion,
    )

    if is_must_visit and accept >= 0.35:
        status = "must_visit"
    elif accept < 0.35 or (eff_aversion >= 0.7 and crowd >= 0.5):
        status = "likely_skip"
        if not any("Crowd-averse" in r for r in reasons):
            reasons.append("Low visit probability at current crowding")
    elif crowd >= 0.55:
        status = "caution"
    else:
        status = "recommended"

    return status, reasons, accept


def build_recommendation_insights_for(
    tourist: Tourist,
    strategy: RecommenderStrategy,
    pois: list[POI],
    crowding: dict[str, CrowdingState],
    *,
    soft_threshold: float = 0.5,
    steepness: float = 5.0,
    top_k: int = 5,
    must_visit_poi_ids: frozenset[str] = frozenset(),
) -> list[RecommendationInsight]:
    recs = strategy.recommend(
        tourist, pois, crowding, top_k=top_k + len(must_visit_poi_ids)
    )
    poi_by_id = {p.poi_id: p for p in pois}
    rec_by_id = {r.poi.poi_id: r for r in recs}

    ordered_ids: list[str] = []
    for poi_id in must_visit_poi_ids:
        if poi_id not in ordered_ids:
            ordered_ids.append(poi_id)
    for rec in recs:
        if rec.poi.poi_id not in ordered_ids:
            ordered_ids.append(rec.poi.poi_id)

    insights: list[RecommendationInsight] = []
    for poi_id in ordered_ids[:top_k]:
        poi = poi_by_id.get(poi_id)
        if poi is None:
            continue
        is_must = poi_id in must_visit_poi_ids
        state = crowding.get(poi_id) or CrowdingState(
            poi_id=poi_id,
            capacity=poi.capacity,
            baseline_intensity=poi.baseline_tourism_intensity,
        )
        dist = haversine_km(tourist.lat, tourist.lon, poi.lat, poi.lon)
        exclusion = poi_exclusion_reason(tourist, poi, crowding)

        if exclusion and is_must:
            over_budget = "budget" in exclusion.lower()
            insights.append(
                RecommendationInsight(
                    rank=len(insights) + 1,
                    poi_name=poi.name,
                    score=0.0,
                    crowd_pct=state.combined_crowding,
                    distance_km=dist,
                    status="blocked",
                    reasons=[f"Must visit — but {exclusion.lower()}"],
                    accept_pct=0.0,
                    entry_price=entry_price_for_card(poi),
                    budget_limit=f"€{tourist.max_price_eur:.0f}" if over_budget else "",
                )
            )
            continue

        if exclusion:
            continue

        rec = rec_by_id.get(poi_id)
        if rec is None:
            rec = Recommendation(poi=poi, score=0.5 if is_must else 0.0)

        status, reasons, accept = _status_for(
            rec,
            tourist,
            state,
            soft_threshold=soft_threshold,
            steepness=steepness,
            is_must_visit=is_must,
        )
        insights.append(
            RecommendationInsight(
                rank=len(insights) + 1,
                poi_name=rec.poi.name,
                score=rec.score,
                crowd_pct=state.combined_crowding,
                distance_km=dist,
                status=status,
                reasons=reasons[:5],
                accept_pct=accept,
                entry_price=entry_price_for_card(rec.poi),
            )
        )
    return insights


def build_recommendation_insights(
    model: TourismModel,
    tourist: Tourist,
    top_k: int = 5,
) -> list[RecommendationInsight]:
    return build_recommendation_insights_for(
        tourist,
        model.strategy,
        model.pois,
        model.crowding,
        soft_threshold=model.soft_threshold,
        steepness=model.accept_steepness,
        top_k=top_k,
    )


def top_crowded_pois(model: TourismModel, pois: list[POI], n: int = 8) -> list[CrowdedPOI]:
    poi_by_id = {p.poi_id: p for p in pois}
    ranked = sorted(
        model.crowding.items(),
        key=lambda kv: kv[1].combined_crowding,
        reverse=True,
    )
    out: list[CrowdedPOI] = []
    for poi_id, state in ranked[:n]:
        poi = poi_by_id.get(poi_id)
        if not poi:
            continue
        out.append(
            CrowdedPOI(
                name=poi.name,
                crowd_pct=state.combined_crowding,
                visits_today=state.visits_today,
                district=poi.district or "—",
            )
        )
    return out


def compare_strategies_for_tourist(
    tourist: Tourist,
    pois: list[POI],
    crowding: dict[str, CrowdingState],
    strategy_a: str,
    strategy_b: str,
    top_k: int = 3,
) -> dict[str, list[str]]:
    """Return top POI names for two strategies (same live state)."""
    sa = get_strategy(strategy_a)
    sb = get_strategy(strategy_b)
    return {
        strategy_a: [r.poi.name for r in sa.recommend(tourist, pois, crowding, top_k=top_k)],
        strategy_b: [r.poi.name for r in sb.recommend(tourist, pois, crowding, top_k=top_k)],
    }
