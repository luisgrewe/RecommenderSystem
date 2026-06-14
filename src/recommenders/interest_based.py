"""Interest-based recommender with tag cosine similarity and penalties."""

from __future__ import annotations

import math

from src.models import CrowdingState, POI, Recommendation, Tourist
from src.recommenders.base import filter_valid_pois
from src.recommenders.trip_profile import (
    family_distance_penalty_multiplier,
    group_type_score_adjustment,
    pace_crowd_score_multiplier,
    pace_distance_penalty_multiplier,
    trip_pace_score_adjustment,
)
from src.simulation.geo import haversine_km


def _tag_vector(tags: frozenset[str], vocabulary: list[str]) -> list[float]:
    return [1.0 if tag in tags else 0.0 for tag in vocabulary]


def cosine_similarity(a: frozenset[str], b: frozenset[str]) -> float:
    vocabulary = sorted(a | b)
    if not vocabulary:
        return 0.0
    vec_a = _tag_vector(a, vocabulary)
    vec_b = _tag_vector(b, vocabulary)
    dot = sum(x * y for x, y in zip(vec_a, vec_b, strict=True))
    norm_a = math.sqrt(sum(x * x for x in vec_a))
    norm_b = math.sqrt(sum(x * x for x in vec_b))
    if norm_a == 0 or norm_b == 0:
        return 0.0
    return dot / (norm_a * norm_b)


class InterestBasedRecommender:
    name = "interest_based"

    def recommend(
        self,
        tourist: Tourist,
        pois: list[POI],
        crowding: dict[str, CrowdingState],
        top_k: int = 5,
    ) -> list[Recommendation]:
        valid = filter_valid_pois(tourist, pois, crowding)
        scored: list[tuple[POI, float]] = []

        for poi in valid:
            interest = cosine_similarity(tourist.interest_tags, poi.interest_tags)
            distance = haversine_km(tourist.lat, tourist.lon, poi.lat, poi.lon)
            distance_penalty = min(
                0.4,
                distance
                / tourist.travel_budget_km
                * 0.3
                * family_distance_penalty_multiplier(tourist)
                * pace_distance_penalty_multiplier(tourist),
            )

            crowd_penalty = 0.0
            state = crowding.get(poi.poi_id)
            crowd_pct = 0.0
            if state:
                crowd_pct = state.combined_crowding
                crowd_penalty = (
                    crowd_pct
                    * 0.25
                    * tourist.crowd_aversion
                    * pace_crowd_score_multiplier(tourist)
                )

            score = max(
                0.0,
                interest
                - distance_penalty
                - crowd_penalty
                + group_type_score_adjustment(tourist, poi)
                + trip_pace_score_adjustment(
                    tourist, poi, distance_km=distance, crowd_pct=crowd_pct
                ),
            )
            scored.append((poi, score))

        scored.sort(key=lambda item: item[1], reverse=True)
        return [Recommendation(poi=p, score=s) for p, s in scored[:top_k]]
