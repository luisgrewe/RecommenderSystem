"""Visit acceptance and soft crowding utility."""

from __future__ import annotations

import math

from src.models import CrowdingState, POI


def soft_crowding_utility(crowding: float, threshold: float = 0.6) -> float:
    """Smooth utility decrease as crowding exceeds soft threshold."""
    if crowding <= threshold:
        return 1.0
    excess = (crowding - threshold) / max(1e-6, 1.0 - threshold)
    return max(0.0, 1.0 - excess**2)


def accept_probability(
    recommendation_score: float,
    crowding_state: CrowdingState,
    *,
    soft_threshold: float = 0.6,
    steepness: float = 4.0,
    crowd_aversion: float = 0.3,
) -> float:
    """Logistic acceptance from score and live crowding."""
    crowd_util = soft_crowding_utility(crowding_state.combined_crowding, soft_threshold)
    # Higher crowd_aversion amplifies the impact of low crowd utility.
    effective_crowd = 1.0 - crowd_aversion * (1.0 - crowd_util)
    adjusted = recommendation_score * effective_crowd
    return 1.0 / (1.0 + math.exp(-steepness * (adjusted - 0.35)))


def visit_utility(poi: POI, crowding_state: CrowdingState, interest_match: float) -> float:
    """Post-visit satisfaction proxy."""
    crowd_factor = soft_crowding_utility(crowding_state.combined_crowding)
    return 0.6 * interest_match + 0.4 * crowd_factor
