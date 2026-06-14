"""Recommender strategy registry."""

from __future__ import annotations

from src.recommenders.base import RecommenderStrategy
from src.recommenders.interest_based import InterestBasedRecommender
from src.recommenders.popularity import PopularityRecommender
from src.recommenders.sustainability import SustainabilityRecommender

STRATEGIES: dict[str, RecommenderStrategy] = {
    "popularity": PopularityRecommender(),
    "interest_based": InterestBasedRecommender(),
    "sustainability": SustainabilityRecommender(),
}


def get_strategy(name: str) -> RecommenderStrategy:
    if name not in STRATEGIES:
        raise KeyError(f"Unknown strategy: {name}. Available: {list(STRATEGIES)}")
    return STRATEGIES[name]
