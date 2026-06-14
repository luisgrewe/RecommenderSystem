"""Recommendation quality metrics."""

from __future__ import annotations

from src.models import POI, Recommendation, Tourist


def profile_consistency(recommendations: list[Recommendation], tourist: Tourist) -> float:
    """Fraction of recommended POIs sharing at least one interest tag."""
    if not recommendations:
        return 0.0
    matches = sum(
        1 for rec in recommendations if rec.poi.interest_tags & tourist.interest_tags
    )
    return matches / len(recommendations)


def tag_precision_recall(
    recommendations: list[Recommendation],
    tourist: Tourist,
) -> tuple[float, float]:
    if not recommendations:
        return 0.0, 0.0
    rec_tags: set[str] = set()
    for rec in recommendations:
        rec_tags |= set(rec.poi.interest_tags)
    tourist_tags = set(tourist.interest_tags)
    if not rec_tags:
        return 0.0, 0.0
    overlap = rec_tags & tourist_tags
    precision = len(overlap) / len(rec_tags)
    recall = len(overlap) / len(tourist_tags) if tourist_tags else 0.0
    return precision, recall


def recommendation_diversity(recommendations: list[Recommendation]) -> float:
    """Unique tag count normalised by list length."""
    if not recommendations:
        return 0.0
    all_tags: set[str] = set()
    for rec in recommendations:
        all_tags |= set(rec.poi.interest_tags)
    return len(all_tags) / len(recommendations)
