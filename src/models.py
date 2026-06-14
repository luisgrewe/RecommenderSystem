"""Core dataclasses shared across data, recommenders, and simulation."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class POI:
    """Point of interest used by recommenders and the ABM."""

    poi_id: str
    name: str
    lat: float
    lon: float
    district: str = ""
    neighborhood: str = ""
    price_eur: float | None = None
    interest_tags: frozenset[str] = frozenset()
    popularity_score: float = 0.5
    sustainability_score: float = 0.5
    baseline_tourism_intensity: float = 0.5
    capacity: int = 500
    outstanding: bool = False

    def to_dict(self) -> dict[str, Any]:
        return {
            "poi_id": self.poi_id,
            "name": self.name,
            "lat": self.lat,
            "lon": self.lon,
            "district": self.district,
            "neighborhood": self.neighborhood,
            "price_eur": self.price_eur,
            "interest_tags": "|".join(sorted(self.interest_tags)),
            "popularity_score": self.popularity_score,
            "sustainability_score": self.sustainability_score,
            "baseline_tourism_intensity": self.baseline_tourism_intensity,
            "capacity": self.capacity,
            "outstanding": self.outstanding,
        }


@dataclass(frozen=True)
class Tourist:
    """Tourist profile for recommendation and agent initialization."""

    tourist_id: str
    interest_tags: frozenset[str]
    max_price_eur: float
    travel_budget_km: float
    lat: float
    lon: float
    crowd_aversion: float = 0.3
    sustainability_sensitivity: float = 0.5
    prefers_outdoor: bool = False
    travel_with_kids: bool = False
    trip_pace: str = "standard"  # relaxed | standard | packed
    group_type: str = "solo"  # solo | couple | family | group
    walking_tolerance: str = "medium"  # low / medium / high


@dataclass
class ScoreBreakdown:
    """Explainable MCDA components for sustainability recommender."""

    interest: float = 0.0
    environment: float = 0.0
    culture: float = 0.0
    economy: float = 0.0
    crowding_dispersion: float = 0.0
    crowd_penalty: float = 0.0
    distance_penalty: float = 0.0
    total: float = 0.0

    def as_dict(self) -> dict[str, float]:
        return {
            "interest": self.interest,
            "environment": self.environment,
            "culture": self.culture,
            "economy": self.economy,
            "crowding_dispersion": self.crowding_dispersion,
            "crowd_penalty": self.crowd_penalty,
            "distance_penalty": self.distance_penalty,
            "total": self.total,
        }


@dataclass(frozen=True)
class Recommendation:
    """Ranked POI suggestion for a tourist."""

    poi: POI
    score: float
    breakdown: ScoreBreakdown | None = None


@dataclass
class CrowdingState:
    """Live crowding snapshot for one POI."""

    poi_id: str
    visits_today: int = 0
    capacity: int = 500
    baseline_intensity: float = 0.5

    @property
    def load_ratio(self) -> float:
        if self.capacity <= 0:
            return 1.0
        return min(1.0, self.visits_today / self.capacity)

    @property
    def combined_crowding(self) -> float:
        """Blend baseline spatial intensity with live visit load."""
        return min(1.0, 0.4 * self.baseline_intensity + 0.6 * self.load_ratio)
