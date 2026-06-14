"""Popularity-based recommender (TripAdvisor-style hotspot ranking)."""

from __future__ import annotations

from src.models import CrowdingState, POI, Recommendation, Tourist
from src.recommenders.base import filter_valid_pois
from src.recommenders.trip_profile import group_type_score_adjustment, trip_pace_score_adjustment
from src.simulation.geo import haversine_km


class PopularityRecommender:
    name = "popularity"

    def _rank_score(
        self,
        tourist: Tourist,
        poi: POI,
        crowding: dict[str, CrowdingState],
    ) -> float:
        state = crowding.get(poi.poi_id)
        crowd_pct = state.combined_crowding if state else poi.baseline_tourism_intensity
        distance = haversine_km(tourist.lat, tourist.lon, poi.lat, poi.lon)
        return (
            poi.popularity_score
            + group_type_score_adjustment(tourist, poi)
            + trip_pace_score_adjustment(
                tourist, poi, distance_km=distance, crowd_pct=crowd_pct
            )
        )

    def recommend(
        self,
        tourist: Tourist,
        pois: list[POI],
        crowding: dict[str, CrowdingState],
        top_k: int = 5,
    ) -> list[Recommendation]:
        valid = filter_valid_pois(tourist, pois, crowding)
        ranked = sorted(
            valid,
            key=lambda p: self._rank_score(tourist, p, crowding),
            reverse=True,
        )
        return [Recommendation(poi=p, score=p.popularity_score) for p in ranked[:top_k]]
