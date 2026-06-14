"""Trip pace and group type adjustments for recommenders and visit acceptance."""

from __future__ import annotations

from typing import Any

from src.models import POI, Tourist

OUTDOOR_TAGS = frozenset({"park", "nature", "sport", "viewpoint"})
CULTURE_TAGS = frozenset({"architecture", "history", "viewpoint", "religious"})

PACE_CROWD_BONUS: dict[str, float] = {
    "relaxed": 0.15,
    "standard": 0.0,
    "packed": -0.12,
}

GROUP_CROWD_BONUS: dict[str, float] = {
    "solo": 0.0,
    "couple": 0.0,
    "family": 0.08,
    "group": 0.12,
}

PACE_STEEPNESS: dict[str, float] = {
    "relaxed": 0.85,
    "standard": 1.0,
    "packed": 1.15,
}

PACE_DISTANCE_MULT: dict[str, float] = {
    "relaxed": 1.35,
    "standard": 1.0,
    "packed": 0.72,
}

PACE_CROWD_SCORE_MULT: dict[str, float] = {
    "relaxed": 1.5,
    "standard": 1.0,
    "packed": 0.55,
}

TRIP_PACE_LABELS: dict[str, str] = {
    "relaxed": "Relaxed",
    "standard": "Standard",
    "packed": "Packed",
}

GROUP_TYPE_LABELS: dict[str, str] = {
    "solo": "Solo",
    "couple": "Couple",
    "family": "Family",
    "group": "Group",
}


class TouristView:
    """Proxy Tourist with trip pace/group — survives Solara hot-reload of models."""

    __slots__ = ("_base", "trip_pace", "group_type")

    def __init__(self, base: Tourist, trip_pace: str, group_type: str) -> None:
        object.__setattr__(self, "_base", base)
        object.__setattr__(self, "trip_pace", trip_pace)
        object.__setattr__(self, "group_type", group_type)

    def __getattr__(self, name: str) -> Any:
        return getattr(self._base, name)


def trip_pace_of(tourist: Tourist) -> str:
    return getattr(tourist, "trip_pace", "standard")


def group_type_of(tourist: Tourist) -> str:
    return getattr(tourist, "group_type", "solo")


def attach_trip_context(tourist: Tourist, *, trip_pace: str, group_type: str) -> Tourist:
    """Return tourist with pace/group attached for recommenders."""
    from dataclasses import fields, replace

    names = {f.name for f in fields(Tourist)}
    if "trip_pace" in names and "group_type" in names:
        return replace(tourist, trip_pace=trip_pace, group_type=group_type)
    return TouristView(tourist, trip_pace, group_type)  # type: ignore[return-value]


def effective_crowd_aversion(tourist: Tourist) -> float:
    """Pace and group type shift how much crowding affects acceptance."""
    pace = PACE_CROWD_BONUS.get(trip_pace_of(tourist), 0.0)
    group = GROUP_CROWD_BONUS.get(group_type_of(tourist), 0.0)
    return min(1.0, max(0.0, tourist.crowd_aversion + pace + group))


def accept_steepness_for(tourist: Tourist, base_steepness: float) -> float:
    """Packed trips accept recommendations more readily; relaxed trips less so."""
    factor = PACE_STEEPNESS.get(trip_pace_of(tourist), 1.0)
    return base_steepness * factor


def pace_distance_penalty_multiplier(tourist: Tourist) -> float:
    return PACE_DISTANCE_MULT.get(trip_pace_of(tourist), 1.0)


def pace_crowd_score_multiplier(tourist: Tourist) -> float:
    return PACE_CROWD_SCORE_MULT.get(trip_pace_of(tourist), 1.0)


def trip_pace_score_adjustment(
    tourist: Tourist,
    poi: POI,
    *,
    distance_km: float,
    crowd_pct: float,
) -> float:
    """Direct ranking nudge — relaxed favours nearby/quiet; packed favours famous/busy."""
    pace = trip_pace_of(tourist)
    adj = 0.0

    if pace == "relaxed":
        if distance_km <= min(2.5, tourist.travel_budget_km * 0.35):
            adj += 0.10
        if crowd_pct < 0.25:
            adj += 0.08
        elif crowd_pct >= 0.40:
            adj -= 0.12
        if poi.baseline_tourism_intensity >= 0.70:
            adj -= 0.06
    elif pace == "packed":
        if poi.popularity_score >= 0.60:
            adj += 0.10
        if crowd_pct >= 0.30:
            adj += 0.05
        if distance_km > tourist.travel_budget_km * 0.45:
            adj += 0.04

    return adj


def group_type_score_adjustment(tourist: Tourist, poi: POI) -> float:
    """Soft score nudge by who is travelling — modest so strategies stay distinct."""
    tags = poi.interest_tags
    gt = group_type_of(tourist)
    adj = 0.0

    if gt == "family":
        if tags & OUTDOOR_TAGS or poi.price_eur == 0:
            adj += 0.15
        if poi.price_eur and poi.price_eur > tourist.max_price_eur * 0.65:
            adj -= 0.05
        if "museum" in tags and not (tags & OUTDOOR_TAGS):
            adj -= 0.10
    elif gt == "group":
        if poi.capacity >= 600 or tags & OUTDOOR_TAGS:
            adj += 0.06
        if poi.baseline_tourism_intensity > 0.75:
            adj -= 0.04
    elif gt == "couple":
        if tags & CULTURE_TAGS:
            adj += 0.05
    elif gt == "solo":
        if poi.popularity_score < 0.5 and poi.baseline_tourism_intensity < 0.5:
            adj += 0.06

    return adj


def family_distance_penalty_multiplier(tourist: Tourist) -> float:
    """Families penalise long hops between POIs a bit more."""
    return 1.25 if group_type_of(tourist) == "family" else 1.0


def trip_profile_reasons(tourist: Tourist, poi: POI) -> list[str]:
    """Explainable hints for recommendation cards."""
    reasons: list[str] = []
    gt = group_type_of(tourist)
    pace = trip_pace_of(tourist)
    tags = poi.interest_tags

    if gt == "family":
        if tags & OUTDOOR_TAGS or poi.price_eur == 0:
            reasons.append("Family-friendly — outdoor or free entry")
        elif "museum" in tags and not (tags & OUTDOOR_TAGS):
            reasons.append("Indoor-only museum — harder with family")
    elif gt == "group":
        reasons.append("Group trip — prefers space and lower crowding pressure")
    elif gt == "couple" and tags & CULTURE_TAGS:
        reasons.append("Couple trip — culture and viewpoints rank higher")
    elif gt == "solo" and poi.popularity_score < 0.5:
        reasons.append("Solo trip — quieter, lesser-known spots favoured")

    if pace == "relaxed":
        reasons.append("Relaxed pace — less likely to visit if crowded or far")
    elif pace == "packed":
        reasons.append("Packed pace — more willing to visit even when busy")

    return reasons
