"""Tests for strategy ↔ profile connection help text."""

from src.viz.profile_help import (
    interests_hint,
    recommendations_panel_note,
    strategy_field_matrix,
    sustainability_focus_hint,
)


def test_interests_matter_for_interest_based():
    assert "Main driver" in interests_hint("interest_based")


def test_interests_ignored_for_popularity():
    assert "Not used for ranking" in interests_hint("popularity")


def test_sustainability_focus_only_strong_for_sustainability_strategy():
    assert "Strong effect" in sustainability_focus_hint("sustainability")
    assert "Little effect" in sustainability_focus_hint("popularity")


def test_recommendations_note_names_strategy():
    text = recommendations_panel_note("sustainability")
    assert "Sustainability-aware" in text
    assert "Your trip" in text


def test_field_matrix_lists_interests_for_sustainability():
    assert "interests" in strategy_field_matrix("sustainability")
    assert "interests" not in strategy_field_matrix("popularity")
