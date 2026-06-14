"""Explain how Run simulation settings connect to Your trip profile."""

from __future__ import annotations

from src.viz.theme import STRATEGY_LABELS


def your_trip_intro() -> str:
    return (
        "<strong>Two layers</strong>"
        "<p><em>Run simulation</em> — strategy + scenario drive the map, metrics, "
        "and all simulated tourist agents (their interests come from the scenario).</p>"
        "<p><em>Your trip</em> — a separate profile for <strong>Your recommendations</strong> "
        "and the strategy comparison. Same recommender logic, your choices below.</p>"
    )


def interests_hint(strategy_id: str) -> str:
    hints = {
        "popularity": (
            "Not used for ranking — famous POIs win. Budget and distance still filter "
            "what you can reach."
        ),
        "interest_based": (
            "Main driver — the recommender ranks POIs by how well they match these tags."
        ),
        "sustainability": (
            "Part of the score — combined with sustainability focus, crowding, and "
            "spreading visitors across the city."
        ),
    }
    return hints.get(strategy_id, hints["interest_based"])


def crowd_aversion_hint(strategy_id: str) -> str:
    if strategy_id in {"interest_based", "sustainability"}:
        return (
            "Penalises crowded POIs in the score (stronger with Interest-based and "
            "Sustainability-aware). Also lowers how likely you are to actually visit."
        )
    return (
        "Does not change the ranked list for this strategy — only how likely you "
        "would accept a busy POI if recommended."
    )


def sustainability_focus_hint(strategy_id: str) -> str:
    if strategy_id == "sustainability":
        return (
            "Strong effect — amplifies environment and crowding-spread terms in the "
            "Sustainability-aware score."
        )
    return (
        "Little effect with this strategy — mainly used by Sustainability-aware "
        "(switch strategy above to see it matter)."
    )


def recommendations_panel_note(strategy_id: str) -> str:
    label = STRATEGY_LABELS.get(strategy_id, strategy_id)
    return (
        f"Ranked with <strong>{label}</strong> applied to <strong>Your trip</strong> "
        f"(not the simulated crowd). Change strategy above to compare approaches."
    )


def strategy_field_matrix(strategy_id: str) -> str:
    """One-line summary of which Your trip fields affect scoring for this strategy."""
    matrix = {
        "popularity": "Uses: budget · distance · group · pace · must-visit · visit chance",
        "interest_based": (
            "Uses: interests · budget · distance · group · pace · crowd aversion · must-visit"
        ),
        "sustainability": (
            "Uses: interests · budget · distance · group · pace · crowd aversion · "
            "sustainability focus · must-visit"
        ),
    }
    return matrix.get(strategy_id, matrix["interest_based"])
