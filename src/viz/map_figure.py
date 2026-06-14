"""Plotly map builder for the dashboard."""

from __future__ import annotations

import plotly.graph_objects as go

from src.metrics.crowding import gini_coefficient, hotspot_visit_pct
from src.models import POI
from src.simulation.model import TourismModel, simulation_complete
from src.viz.theme import HOTSPOT_SUBSTRINGS


def _crowd_color(crowding: float) -> str:
    """Green (low) → amber → red (high)."""
    if crowding < 0.35:
        return "#34d399"
    if crowding < 0.65:
        return "#fbbf24"
    return "#f87171"


def build_map_figure(
    pois: list[POI],
    model: TourismModel | None,
    *,
    uirevision: str = "barcelona-map",
) -> go.Figure:
    fig = go.Figure()

    if model is None:
        fig.add_trace(
            go.Scattermapbox(
                lat=[p.lat for p in pois],
                lon=[p.lon for p in pois],
                mode="markers",
                marker=dict(size=8, color="#64748b", opacity=0.7),
                text=[p.name for p in pois],
                hovertemplate="<b>%{text}</b><extra></extra>",
                name="POIs (idle)",
            )
        )
    else:
        sizes = []
        colors = []
        texts = []
        for poi in pois:
            crowd = model.crowding[poi.poi_id].combined_crowding
            visits = model.total_visits.get(poi.poi_id, 0)
            sizes.append(10 + crowd * 22)
            colors.append(_crowd_color(crowd))
            texts.append(
                f"{poi.name}<br>Crowding: {crowd:.0%}<br>Total visits: {visits}"
            )

        fig.add_trace(
            go.Scattermapbox(
                lat=[p.lat for p in pois],
                lon=[p.lon for p in pois],
                mode="markers",
                marker=dict(size=sizes, color=colors, opacity=0.85),
                text=texts,
                hovertemplate="<b>%{text}</b><extra></extra>",
                name="POIs",
            )
        )

        fig.add_trace(
            go.Scattermapbox(
                lat=[a.current_lat for a in model.agents],
                lon=[a.current_lon for a in model.agents],
                mode="markers",
                marker=dict(size=6, color="#38bdf8", opacity=0.55),
                text=["Tourist"] * len(model.agents),
                hoverinfo="skip",
                name="Tourists",
            )
        )

    fig.update_layout(
        mapbox=dict(
            style="open-street-map",
            center=dict(lat=41.387, lon=2.168),
            zoom=11.2,
        ),
        margin=dict(l=0, r=0, t=0, b=0),
        height=560,
        paper_bgcolor="#1a2332",
        plot_bgcolor="#1a2332",
        showlegend=False,
        uirevision=uirevision,
    )
    return fig


def live_metrics(model: TourismModel | None, pois: list[POI]) -> dict[str, str]:
    if model is None:
        return {
            "day": "—",
            "agents": "—",
            "visits": "—",
            "gini": "—",
            "hotspots": "—",
        }

    visit_values = list(model.total_visits.values())
    poi_names = {p.poi_id: p.name for p in pois}
    gini = gini_coefficient(visit_values)
    hotspot = hotspot_visit_pct(model.total_visits, poi_names, HOTSPOT_SUBSTRINGS)

    days_done = len(model.daily_visit_log)
    day_label = f"{days_done} / {model.num_days}"
    if simulation_complete(model):
        day_label += " · done"

    return {
        "day": day_label,
        "agents": str(len(model.agents)),
        "visits": str(sum(visit_values)),
        "gini": f"{gini:.2f}",
        "hotspots": f"{hotspot:.0%}",
    }
