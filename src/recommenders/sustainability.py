"""Sustainability-aware recommender.

The final recommendation score combines:
- interest match: how well the POI matches the tourist's interests;
- environment: preference for POIs in less tourism-saturated areas;
- culture: preference for culturally relevant POIs;
- economy: preference for free or affordable POIs;
- crowding dispersion: preference for POIs that are not currently crowded;
- distance and crowding penalties;
- small trip-profile adjustments, such as group type and trip pace.
"""

from __future__ import annotations

from src.config import load_config
from src.models import CrowdingState, POI, Recommendation, ScoreBreakdown, Tourist
from src.recommenders.base import filter_valid_pois
from src.recommenders.interest_based import cosine_similarity
from src.recommenders.trip_profile import (
    group_type_score_adjustment,
    pace_crowd_score_multiplier,
    pace_distance_penalty_multiplier,
    trip_pace_score_adjustment,
)
from src.simulation.geo import haversine_km


CULTURAL_TAGS = frozenset({"museum", "history", "religious", "architecture"})
DEFAULT_UNKNOWN_PRICE_EUR = 15.0
MAX_PRICE_SCALE_EUR = 40.0


def cultural_relevance_score(poi: POI) -> float:
    """Return a simple cultural relevance score based on POI tags."""
    return 1.0 if poi.interest_tags & CULTURAL_TAGS else 0.6


def affordability_score(poi: POI) -> float:
    """Return an affordability score where free and cheaper POIs score higher."""
    if poi.price_eur == 0:
        return 1.0

    assumed_price = poi.price_eur if poi.price_eur is not None else DEFAULT_UNKNOWN_PRICE_EUR
    return max(0.0, 1.0 - assumed_price / MAX_PRICE_SCALE_EUR)


class SustainabilityRecommender:
    name = "sustainability"

    def __init__(self, weights: dict[str, float] | None = None) -> None:
        if weights is None:
            cfg = load_config()
            weights = cfg["sustainability_weights"]
        self.weights = weights

    def recommend(
        self,
        tourist: Tourist,
        pois: list[POI],
        crowding: dict[str, CrowdingState],
        top_k: int = 5,
    ) -> list[Recommendation]:
        valid = filter_valid_pois(tourist, pois, crowding)
        recommendations: list[Recommendation] = []

        for poi in valid:
            interest = cosine_similarity(tourist.interest_tags, poi.interest_tags)
            environment = 1.0 - poi.baseline_tourism_intensity
            culture = cultural_relevance_score(poi)
            economy = affordability_score(poi)

            state = crowding.get(poi.poi_id)
            live_crowd = state.combined_crowding if state else poi.baseline_tourism_intensity
            crowding_dispersion = 1.0 - live_crowd

            distance = haversine_km(tourist.lat, tourist.lon, poi.lat, poi.lon)
            distance_penalty = min(
                0.15,
                distance
                / tourist.travel_budget_km
                * 0.1
                * pace_distance_penalty_multiplier(tourist),
            )

            beta = tourist.sustainability_sensitivity
            crowd_penalty = live_crowd * 0.1 * beta * pace_crowd_score_multiplier(tourist)

            w = self.weights
            total = (
                w["interest"] * interest
                + w["environment"] * environment * beta
                + w["culture"] * culture
                + w["economy"] * economy
                + w["crowding_dispersion"] * crowding_dispersion * beta
                - distance_penalty
                - crowd_penalty
                + group_type_score_adjustment(tourist, poi)
                + trip_pace_score_adjustment(
                    tourist,
                    poi,
                    distance_km=distance,
                    crowd_pct=live_crowd,
                )
            )

            breakdown = ScoreBreakdown(
                interest=interest,
                environment=environment,
                culture=culture,
                economy=economy,
                crowding_dispersion=crowding_dispersion,
                crowd_penalty=crowd_penalty,
                distance_penalty=distance_penalty,
                total=total,
            )

            recommendations.append(
                Recommendation(poi=poi, score=total, breakdown=breakdown)
            )

        recommendations.sort(key=lambda r: r.score, reverse=True)
        return recommendations[:top_k]