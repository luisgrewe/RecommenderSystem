"""Recommender strategy protocol and shared helpers."""

from __future__ import annotations

from typing import Protocol

from src.models import CrowdingState, POI, Recommendation, Tourist
from src.recommenders.filters import filter_valid_pois, poi_exclusion_reason

__all__ = ["RecommenderStrategy", "filter_valid_pois", "poi_exclusion_reason"]


class RecommenderStrategy(Protocol):
    name: str

    def recommend(
        self,
        tourist: Tourist,
        pois: list[POI],
        crowding: dict[str, CrowdingState],
        top_k: int = 5,
    ) -> list[Recommendation]:
        ...
