"""Tests for City snapshot HTML helpers."""

from src.viz.insights import CrowdedPOI
from src.viz.snapshot import (
    render_crowded_poi_row,
    render_strategy_compare,
)


def test_crowded_row_includes_bar_and_tier():
    row = CrowdedPOI(
        name="Palau Güell",
        crowd_pct=0.4,
        visits_today=12,
        district="Ciutat Vella",
    )
    html = render_crowded_poi_row(1, row)
    assert "crowd-bar-fill moderate" in html
    assert "40% · Busy" in html
    assert "12 visits today" in html
    assert "Ciutat Vella" in html


def test_strategy_compare_two_columns():
    html = render_strategy_compare(
        ["Mercat Boqueria", "Parc de Montjuïc"],
        ["Monestir de Sant Pau del Camp"],
        "Sustainability-aware",
    )
    assert "strategy-compare" in html
    assert "strategy-col popularity" in html
    assert "strategy-col current" in html
    assert "Mercat Boqueria" in html
    assert "Sustainability-aware" in html
