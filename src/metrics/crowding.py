"""Crowding and economic distribution metrics."""

from __future__ import annotations

import math
from collections import Counter

import numpy as np


def gini_coefficient(values: list[int] | np.ndarray) -> float:
    arr = np.array(values, dtype=float)
    if arr.size == 0 or arr.sum() == 0:
        return 0.0
    arr = np.sort(arr)
    n = arr.size
    index = np.arange(1, n + 1)
    return float((2 * np.sum(index * arr) - (n + 1) * np.sum(arr)) / (n * np.sum(arr)))


def visit_entropy(values: list[int] | np.ndarray) -> float:
    arr = np.array(values, dtype=float)
    total = arr.sum()
    if total == 0:
        return 0.0
    probs = arr / total
    probs = probs[probs > 0]
    return float(-np.sum(probs * np.log(probs)))


def hotspot_visit_pct(
    total_visits: dict[str, int],
    poi_names: dict[str, str],
    hotspot_substrings: list[str],
) -> float:
    total = sum(total_visits.values())
    if total == 0:
        return 0.0
    hotspot_visits = 0
    for poi_id, count in total_visits.items():
        name = poi_names.get(poi_id, "")
        if any(sub.lower() in name.lower() for sub in hotspot_substrings):
            hotspot_visits += count
    return hotspot_visits / total


def local_economic_impact(
    total_visits: dict[str, int],
    poi_prices: dict[str, float | None],
) -> float:
    """Proxy spend: visits × ticket price (free POIs contribute 0)."""
    spend = 0.0
    for poi_id, visits in total_visits.items():
        price = poi_prices.get(poi_id)
        if price is None:
            continue
        spend += visits * price
    return spend
