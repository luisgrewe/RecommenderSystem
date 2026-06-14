"""HTML render helpers for the City snapshot panel."""

from __future__ import annotations

import html

from src.viz.insights import CrowdedPOI


def _crowd_tier(crowd_pct: float) -> str:
    if crowd_pct >= 0.65:
        return "high"
    if crowd_pct >= 0.35:
        return "moderate"
    return "low"


def _crowd_label(crowd_pct: float) -> str:
    tier = _crowd_tier(crowd_pct)
    return {"low": "Quiet", "moderate": "Busy", "high": "Crowded"}[tier]


def render_crowded_poi_row(rank: int, row: CrowdedPOI) -> str:
    tier = _crowd_tier(row.crowd_pct)
    name = html.escape(row.name)
    district = html.escape(row.district)
    width = min(100, max(4, round(row.crowd_pct * 100)))
    visits = f"{row.visits_today:,} visit{'s' if row.visits_today != 1 else ''} today"
    return (
        f'<div class="crowded-card">'
        f'<span class="crowded-rank">{rank}</span>'
        f'<div class="crowded-body">'
        f'<div class="crowded-name" title="{name}">{name[:48]}</div>'
        f'<div class="crowd-bar-track">'
        f'<div class="crowd-bar-fill {tier}" style="width:{width}%"></div>'
        f"</div>"
        f'<div class="crowded-stats">'
        f'<span class="crowd-pill {tier}">{row.crowd_pct:.0%} · {_crowd_label(row.crowd_pct)}</span>'
        f"<span>{visits}</span>"
        f'<span class="district-chip">{district}</span>'
        f"</div></div></div>"
    )


def render_crowded_section(rows: list[CrowdedPOI]) -> str:
    if not rows:
        return (
            '<div class="snapshot-empty">'
            "No crowding data yet — click Start to populate the city."
            "</div>"
        )
    items = "".join(render_crowded_poi_row(i + 1, row) for i, row in enumerate(rows))
    return (
        '<div class="snapshot-section">'
        '<div class="snapshot-section-head">'
        '<span class="snapshot-icon" aria-hidden="true">📍</span>'
        "<div>"
        '<div class="snapshot-section-title">Busiest POIs right now</div>'
        '<div class="snapshot-section-sub">Ranked by live crowding from the simulation</div>'
        "</div></div>"
        f'<div class="crowded-list">{items}</div>'
        "</div>"
    )


def render_strategy_compare(
    popularity_names: list[str],
    current_names: list[str],
    current_label: str,
) -> str:
    def _col(names: list[str], css_class: str, title: str) -> str:
        if not names:
            items = '<li class="strategy-poi-empty">No matches in current filters</li>'
        else:
            items = "".join(
                f'<li><span class="strategy-poi-rank">{i + 1}</span>'
                f"{html.escape(name[:50])}</li>"
                for i, name in enumerate(names)
            )
        return (
            f'<div class="strategy-col {css_class}">'
            f'<div class="strategy-col-title">{html.escape(title)}</div>'
            f"<ul>{items}</ul></div>"
        )

    pop_col = _col(popularity_names, "popularity", "Popularity-based")
    cur_col = _col(current_names, "current", current_label)
    return (
        '<div class="snapshot-section strategy-section">'
        '<div class="snapshot-section-head">'
        '<span class="snapshot-icon" aria-hidden="true">⚖️</span>'
        "<div>"
        '<div class="snapshot-section-title">Your trip — strategy comparison</div>'
        '<div class="snapshot-section-sub">Top 3 picks for your profile with today\'s crowding</div>'
        "</div></div>"
        f'<div class="strategy-compare">{pop_col}{cur_col}</div>'
        "</div>"
    )


def render_snapshot_placeholder() -> str:
    return (
        '<div class="snapshot-placeholder">'
        '<div class="snapshot-placeholder-icon" aria-hidden="true">🗺️</div>'
        "<strong>Start the simulation</strong>"
        "<p>Click Start, then Next day to see which POIs fill up and how strategy "
        "choices change where you would be sent.</p>"
        "</div>"
    )
