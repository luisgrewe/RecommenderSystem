"""Shared POI eligibility filters for recommenders and the dashboard."""

from __future__ import annotations

from src.models import CrowdingState, POI, Tourist
from src.simulation.geo import haversine_km


def poi_exclusion_reason(
    tourist: Tourist,
    poi: POI,
    crowding: dict[str, CrowdingState] | None = None,
    *,
    max_crowding: float = 0.95,
) -> str | None:
    """Return why a POI is filtered out, or None if it is reachable."""
    if poi.price_eur is not None and poi.price_eur > tourist.max_price_eur:
        return f"Over budget (€{poi.price_eur:.0f} entry > €{tourist.max_price_eur:.0f} max per POI)"
    distance = haversine_km(tourist.lat, tourist.lon, poi.lat, poi.lon)
    if distance > tourist.travel_budget_km:
        return f"Too far ({distance:.1f} km > {tourist.travel_budget_km:.1f} km per visit)"
    if tourist.walking_tolerance == "low" and distance > 2.0:
        return f"Long walk ({distance:.1f} km) — limited mobility"
    if crowding is not None:
        state = crowding.get(poi.poi_id)
        if state and state.combined_crowding >= max_crowding:
            return "Filtered (extreme crowding)"
    return None


def filter_valid_pois(
    tourist: Tourist,
    pois: list[POI],
    crowding: dict[str, CrowdingState] | None = None,
    max_crowding: float = 0.95,
) -> list[POI]:
    """Budget, distance, mobility, and crowding filter shared by all strategies."""
    valid: list[POI] = []
    for poi in pois:
        if poi_exclusion_reason(tourist, poi, crowding, max_crowding=max_crowding) is None:
            valid.append(poi)
    return valid
