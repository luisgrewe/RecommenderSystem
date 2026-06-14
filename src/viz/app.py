"""Solara dashboard: Barcelona sustainable tourism ABM."""

from __future__ import annotations

import sys
from pathlib import Path

import plotly.graph_objects as go
import solara

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.config import load_config  # noqa: E402
from src.data.pipeline import load_processed_pois  # noqa: E402
from src.recommenders.registry import get_strategy  # noqa: E402
from src.scenarios import get_scenario, list_scenarios  # noqa: E402
from src.simulation.model import TourismModel, simulation_complete  # noqa: E402
from src.simulation.population import spawn_tourists  # noqa: E402
from src.viz.insights import (  # noqa: E402
    baseline_crowding,
    build_recommendation_insights_for,
    compare_strategies_for_tourist,
    top_crowded_pois,
)
from src.viz.help_text import (  # noqa: E402
    SCENARIO_HELP_EXTRA,
    strategy_help_for,
)
from src.viz.map_figure import build_map_figure, live_metrics  # noqa: E402
from src.viz.profile_help import (  # noqa: E402
    crowd_aversion_hint,
    interests_hint,
    recommendations_panel_note,
    strategy_field_matrix,
    sustainability_focus_hint,
    your_trip_intro,
)
from src.viz.snapshot import (  # noqa: E402
    render_crowded_section,
    render_snapshot_placeholder,
    render_strategy_compare,
)
from src.viz.theme import GLOBAL_CSS, STRATEGY_LABELS  # noqa: E402
from src.viz.user_profile import (  # noqa: E402
    DEFAULT_ENTRY_PRICE,
    DEFAULT_GROUP_TYPE,
    DEFAULT_TRAVEL_RANGE,
    DEFAULT_TRIP_PACE,
    ENTRY_PRICE_OPTIONS,
    GROUP_TYPE_OPTIONS,
    TRAVEL_RANGE_OPTIONS,
    TRIP_PACE_OPTIONS,
    build_viewer_trip,
    interest_tag_labels,
    poi_choices,
    profile_summary,
    tourist_for_recommendations,
)

BASE_CFG = load_config()
POIS = load_processed_pois(BASE_CFG["paths"]["processed_pois"])
SCENARIO_NAMES = [name for name, _ in list_scenarios()]
STRATEGY_IDS = list(BASE_CFG["recommenders"]["strategies"])
STRATEGY_OPTIONS = [STRATEGY_LABELS.get(s, s) for s in STRATEGY_IDS]
INTEREST_OPTIONS = interest_tag_labels(POIS)
POI_OPTIONS, POI_LABEL_TO_ID = poi_choices(POIS)
DEFAULT_INTERESTS = [
    label
    for label in INTEREST_OPTIONS
    if label in {"Religious sites", "Architecture", "History"}
]


def _strategy_id(label: str) -> str:
    for sid, lbl in STRATEGY_LABELS.items():
        if lbl == label:
            return sid
    return label


def _make_model(
    scenario_name: str = "baseline",
    strategy_name: str = "sustainability",
    num_tourists: int | None = None,
    num_days: int | None = None,
    seed: int = 42,
) -> TourismModel:
    cfg = get_scenario(scenario_name)
    if num_tourists is not None:
        cfg["simulation"]["num_tourists"] = num_tourists
    if num_days is not None:
        cfg["simulation"]["num_days"] = num_days

    tourists = spawn_tourists(POIS, cfg, scenario_name, seed=seed)
    strategy = get_strategy(strategy_name)
    crowding_cfg = cfg["crowding"]
    sim = cfg["simulation"]

    return TourismModel(
        pois=POIS,
        tourists=tourists,
        strategy=strategy,
        num_days=sim["num_days"],
        daily_pois_per_tourist=sim["daily_pois_per_tourist"],
        soft_threshold=crowding_cfg["soft_threshold"],
        accept_steepness=crowding_cfg["accept_steepness"],
        decay_rate=crowding_cfg["decay_rate"],
        top_k=cfg["recommenders"]["top_k"],
        seed=seed,
        initial_load_boost=crowding_cfg.get("initial_load_boost", 0.0),
    )


scenario_state = solara.reactive("baseline")
strategy_label_state = solara.reactive(STRATEGY_LABELS["sustainability"])
num_tourists_state = solara.reactive(200)
num_days_state = solara.reactive(BASE_CFG["simulation"]["num_days"])
model_state = solara.reactive(None)
step_count = solara.reactive(0)

# Your trip profile (personalised recommendations)
interest_labels_state = solara.reactive(list(DEFAULT_INTERESTS))
must_visit_labels_state = solara.reactive([])
entry_price_state = solara.reactive(DEFAULT_ENTRY_PRICE)
travel_range_state = solara.reactive(DEFAULT_TRAVEL_RANGE)
crowd_aversion_state = solara.reactive(0.3)
sustainability_state = solara.reactive(0.5)
trip_pace_state = solara.reactive(DEFAULT_TRIP_PACE)
group_type_state = solara.reactive(DEFAULT_GROUP_TYPE)


def _current_strategy_id() -> str:
    return _strategy_id(strategy_label_state.value)


def _build_you_trip():
    return build_viewer_trip(
        interest_labels=interest_labels_state.value,
        entry_price_label=entry_price_state.value,
        travel_range_label=travel_range_state.value,
        trip_pace_label=trip_pace_state.value,
        group_type_label=group_type_state.value,
        crowd_aversion=crowd_aversion_state.value,
        sustainability_sensitivity=sustainability_state.value,
        must_visit_labels=must_visit_labels_state.value,
        pois=POIS,
        label_to_poi_id=POI_LABEL_TO_ID,
    )


def _recommendation_context():
    model = model_state.value
    if model is not None:
        return (
            model.crowding,
            model.soft_threshold,
            model.accept_steepness,
            model.strategy,
        )
    crowding_cfg = BASE_CFG["crowding"]
    return (
        baseline_crowding(POIS),
        crowding_cfg["soft_threshold"],
        crowding_cfg["accept_steepness"],
        get_strategy(_current_strategy_id()),
    )


def _run() -> None:
    model_state.set(
        _make_model(
            scenario_name=scenario_state.value,
            strategy_name=_current_strategy_id(),
            num_tourists=num_tourists_state.value,
            num_days=num_days_state.value,
        )
    )
    step_count.set(0)


def _reset() -> None:
    _run()


def _step() -> None:
    if model_state.value is None:
        _run()
    model = model_state.value
    if simulation_complete(model):
        return
    model.step()
    step_count.set(step_count.value + 1)
    model_state.set(model)


def _run_day() -> None:
    if model_state.value is None:
        _run()
    model = model_state.value
    if simulation_complete(model):
        return
    for _ in range(model.daily_pois_per_tourist):
        if simulation_complete(model):
            break
        model.step()
    model.end_of_day()
    step_count.set(step_count.value + model.daily_pois_per_tourist)
    model_state.set(model)


def _render_rec_item(insight) -> str:
    badge_cls = insight.status
    badge_label = {
        "recommended": "Visit recommended",
        "caution": "Visit with caution",
        "likely_skip": "Likely skipped",
        "must_visit": "Must visit",
        "blocked": "Cannot reach",
    }.get(insight.status, insight.status)
    reasons = "<br>".join(f"• {r}" for r in insight.reasons) if insight.reasons else ""
    if insight.status == "blocked" and insight.budget_limit:
        meta = (
            f"Entry {insight.entry_price} · Your limit {insight.budget_limit} · "
            f"{insight.distance_km:.1f} km"
        )
    elif insight.status == "blocked":
        meta = f"Entry {insight.entry_price} · {insight.distance_km:.1f} km"
    else:
        meta = (
            f"Entry {insight.entry_price} · Score {insight.score:.2f} · "
            f"Crowding {insight.crowd_pct:.0%} · {insight.distance_km:.1f} km · "
            f"Visit chance {insight.accept_pct:.0%}"
        )
    return (
        f'<div class="rec-item {insight.status}">'
        f'<span class="badge {badge_cls}">{badge_label}</span>'
        f'<div class="rec-title">{insight.rank}. {insight.poi_name[:55]}</div>'
        f'<div class="rec-meta">{meta}</div>'
        f'<div class="rec-reasons">{reasons}</div></div>'
    )


def _render_hint(text: str) -> None:
    line = " ".join(text.split())
    if len(line) > 88:
        line = line[:87] + "…"
    solara.HTML(tag="p", classes=["hint-line"], unsafe_innerHTML=line)


def _render_help_box(text: str, *extra_classes: str) -> None:
    classes = ["help-box", *extra_classes]
    solara.HTML(tag="div", classes=list(classes), unsafe_innerHTML=text)


def _render_field_hint(text: str, *, active: bool) -> None:
    css = "field-active" if active else "field-muted"
    solara.HTML(tag="p", classes=[css], unsafe_innerHTML=text)


def _scenario_hint(scenario_name: str, cfg: dict) -> str:
    return (
        cfg.get("scenario_help")
        or cfg.get("scenario_description", "")
        or SCENARIO_HELP_EXTRA.get(scenario_name, "")
    )


def _render_map_legend() -> None:
    with solara.Div(classes=["legend", "map-legend"]):
        solara.HTML(
            tag="div",
            classes=["legend-item"],
            unsafe_innerHTML=(
                '<span class="legend-dot" style="background:#34d399"></span> Low crowding'
            ),
        )
        solara.HTML(
            tag="div",
            classes=["legend-item"],
            unsafe_innerHTML=(
                '<span class="legend-dot" style="background:#fbbf24"></span> Medium'
            ),
        )
        solara.HTML(
            tag="div",
            classes=["legend-item"],
            unsafe_innerHTML=(
                '<span class="legend-dot" style="background:#f87171"></span> High crowding'
            ),
        )
        solara.HTML(
            tag="div",
            classes=["legend-item"],
            unsafe_innerHTML=(
                '<span class="legend-dot" style="background:#38bdf8"></span> Tourist agents'
            ),
        )


@solara.component
def MetricCard(label: str, value: str, tone: str = "", hint: str = ""):
    tone_class = f" {tone}" if tone else ""
    with solara.Div(classes=["metric-card"]):
        solara.HTML(tag="div", classes=["label"], unsafe_innerHTML=label)
        solara.HTML(tag="div", classes=[f"value{tone_class}"], unsafe_innerHTML=value)
        if hint:
            solara.HTML(tag="div", classes=["metric-hint"], unsafe_innerHTML=hint)


def _invalidate_simulation() -> None:
    """Drop running model when run configuration changes."""
    model_state.set(None)
    step_count.set(0)


@solara.component
def Page():
    solara.Style(GLOBAL_CSS)
    solara.use_effect(
        lambda: _invalidate_simulation(),
        [
            scenario_state.value,
            strategy_label_state.value,
            num_tourists_state.value,
            num_days_state.value,
        ],
    )
    cfg = get_scenario(scenario_state.value)
    metrics = live_metrics(model_state.value, POIS)
    map_revision = (
        f"{scenario_state.value}-{_current_strategy_id()}-"
        f"{step_count.value}-{model_state.value is not None}"
    )
    fig = build_map_figure(POIS, model_state.value, uirevision=map_revision)
    map_deps = [map_revision]
    you = _build_you_trip()
    you_tourist = tourist_for_recommendations(you)
    crowding, soft_threshold, steepness, strategy = _recommendation_context()
    your_recs = build_recommendation_insights_for(
        you_tourist,
        strategy,
        POIS,
        crowding,
        soft_threshold=soft_threshold,
        steepness=steepness,
        top_k=5,
        must_visit_poi_ids=you.must_visit_poi_ids,
    )

    gini_tone = ""
    if metrics["gini"] != "—":
        gini_tone = "green" if float(metrics["gini"]) < 0.5 else "warn"

    hotspot_tone = ""
    if metrics["hotspots"] != "—":
        pct = float(metrics["hotspots"].strip("%")) / 100.0
        hotspot_tone = "green" if pct < 0.15 else "danger"

    with solara.Div(classes=["dashboard-root"]):
        with solara.Div(classes=["dashboard-header"]):
            solara.HTML(tag="h1", unsafe_innerHTML="Barcelona Sustainable Tourism ABM")
            solara.HTML(
                tag="p",
                unsafe_innerHTML="Agent-based evaluation of POI recommenders · Open Data BCN",
            )

        with solara.Div(classes=["dashboard-body"]):
            # --- Sidebar ---
            with solara.Div(classes=["sidebar"]):
                with solara.Div(classes=["sidebar section", "sidebar-run"]):
                    solara.HTML(tag="h2", unsafe_innerHTML="Run simulation")
                    solara.Select(
                        label="Scenario",
                        value=scenario_state,
                        values=SCENARIO_NAMES,
                    )
                    _render_hint(_scenario_hint(scenario_state.value, cfg))
                    solara.Select(
                        label="Recommender strategy",
                        value=strategy_label_state,
                        values=STRATEGY_OPTIONS,
                    )
                    _render_field_hint(
                        strategy_help_for(_current_strategy_id()).get("summary", ""),
                        active=True,
                    )
                    _render_field_hint(
                        "Applies to all simulated agents on the map — not Your trip.",
                        active=False,
                    )
                    solara.SliderInt(
                        label="Tourist agents",
                        value=num_tourists_state,
                        min=50,
                        max=500,
                        step=50,
                    )
                    solara.SliderInt(
                        label="Simulation days",
                        value=num_days_state,
                        min=1,
                        max=10,
                        step=1,
                    )
                    with solara.Div(classes=["btn-row", "btn-row-primary"]):
                        solara.Button("▶ Run", on_click=_run, color="primary")
                        solara.Button("↺ Reset", on_click=_reset)
                        solara.Button("Step", on_click=_step)
                        solara.Button("Run day", on_click=_run_day)
                    _render_hint(
                        "Run day advances one day (2 visits per agent) — "
                        "use it to watch crowding build on the map."
                    )

                with solara.Div(classes=["sidebar section"]):
                    solara.HTML(tag="h2", unsafe_innerHTML="Your trip")
                    _render_help_box(your_trip_intro(), "connection")
                    _render_field_hint(
                        strategy_field_matrix(_current_strategy_id()),
                        active=True,
                    )
                    solara.Select(
                        label="Max entry price per POI",
                        value=entry_price_state,
                        values=ENTRY_PRICE_OPTIONS,
                    )
                    _render_hint("Booking-style cap — each ticket must be within this limit.")
                    solara.Select(
                        label="How far per visit",
                        value=travel_range_state,
                        values=TRAVEL_RANGE_OPTIONS,
                    )
                    solara.SelectMultiple(
                        "Interests",
                        interest_labels_state,
                        INTEREST_OPTIONS,
                    )
                    _render_field_hint(
                        interests_hint(_current_strategy_id()),
                        active=_current_strategy_id()
                        in {"interest_based", "sustainability"},
                    )
                    solara.SelectMultiple(
                        "Must-visit places",
                        must_visit_labels_state,
                        POI_OPTIONS,
                    )
                    solara.Select(
                        label="Trip pace",
                        value=trip_pace_state,
                        values=TRIP_PACE_OPTIONS,
                    )
                    _render_field_hint(
                        "Relaxed ranks nearby quiet POIs higher; packed ranks famous "
                        "sights higher — changes the list and visit chance.",
                        active=True,
                    )
                    solara.Select(
                        label="Group type",
                        value=group_type_state,
                        values=GROUP_TYPE_OPTIONS,
                    )
                    _render_field_hint(
                        "Family boosts parks and free entry; group avoids tight crowds; "
                        "solo favours quieter spots — nudges all strategies.",
                        active=True,
                    )
                    solara.SliderFloat(
                        label="Crowd aversion",
                        value=crowd_aversion_state,
                        min=0,
                        max=1,
                        step=0.05,
                    )
                    _render_field_hint(
                        crowd_aversion_hint(_current_strategy_id()),
                        active=_current_strategy_id()
                        in {"interest_based", "sustainability"},
                    )
                    solara.SliderFloat(
                        label="Sustainability focus",
                        value=sustainability_state,
                        min=0,
                        max=1,
                        step=0.05,
                    )
                    _render_field_hint(
                        sustainability_focus_hint(_current_strategy_id()),
                        active=_current_strategy_id() == "sustainability",
                    )

            # --- Main panel ---
            with solara.Div(classes=["main-panel"]):
                with solara.Div(classes=["metrics-row"]):
                    MetricCard("Simulation day", metrics["day"])
                    MetricCard("Active agents", metrics["agents"])
                    MetricCard("Total visits", metrics["visits"])
                    MetricCard(
                        "Crowding Gini",
                        metrics["gini"],
                        tone=gini_tone,
                        hint="0 = even spread · 1 = very concentrated",
                    )
                    MetricCard(
                        "Hotspot share",
                        metrics["hotspots"],
                        tone=hotspot_tone,
                        hint="Only 5 famous sites (Sagrada, Güell…)",
                    )

                solara.HTML(
                    tag="p",
                    classes=["metrics-hint"],
                    unsafe_innerHTML=(
                        "<strong>Gini</strong> measures inequality across all 72 POIs. "
                        "<strong>Hotspot share</strong> is stricter — only visits to five "
                        "famous landmarks count. Low hotspot % with Gini ~0.5–0.6 is normal "
                        "for sustainability: tourists skip the big names but still cluster "
                        "elsewhere. Try <strong>Popularity</strong> to see hotspot share jump."
                    ),
                )

                if model_state.value is None:
                    with solara.Div(classes=["empty-state"]):
                        solara.HTML(
                            tag="p",
                            unsafe_innerHTML=(
                                "<strong>Ready to simulate</strong> — choose a scenario and "
                                "strategy, then click <strong>Run</strong>. "
                                "Changing scenario or strategy resets the map simulation."
                            ),
                        )
                        solara.FigurePlotly(fig, dependencies=map_deps)
                else:
                    with solara.Div(classes=["map-wrap"]):
                        solara.FigurePlotly(fig, dependencies=map_deps)

                _render_map_legend()

                if _current_strategy_id() == "sustainability":
                    solara.HTML(
                        tag="div",
                        classes=["insight-banner"],
                        unsafe_innerHTML=(
                            "<strong>Why little red (high crowding)?</strong> The sustainability "
                            "recommender deliberately steers agents away from hotspots. "
                            "Switch strategy to <strong>Popularity-based</strong> and scenario to "
                            "<strong>overtourism_peak</strong> to see overcrowding build up — "
                            "then compare hotspot % in the metrics."
                        ),
                    )

                with solara.Div(classes=["insights-row"]):
                    with solara.Div(classes=["insights-panel"]):
                        solara.HTML(
                            tag="h3",
                            unsafe_innerHTML="Your recommendations",
                        )
                        solara.HTML(
                            tag="p",
                            classes=["rec-panel-note"],
                            unsafe_innerHTML=recommendations_panel_note(
                                _current_strategy_id()
                            ),
                        )
                        solara.HTML(
                            tag="p",
                            classes=["rec-meta"],
                            unsafe_innerHTML=profile_summary(you, POIS),
                        )
                        if model_state.value is None:
                            solara.HTML(
                                tag="p",
                                classes=["rec-meta"],
                                unsafe_innerHTML=(
                                    "Using baseline crowding — run the simulation "
                                    "to see live hotspot pressure."
                                ),
                            )
                        for ins in your_recs:
                            solara.HTML(
                                tag="div",
                                unsafe_innerHTML=_render_rec_item(ins),
                            )

                    with solara.Div(classes=["insights-panel"]):
                        solara.HTML(tag="h3", unsafe_innerHTML="City snapshot")
                        if model_state.value is None:
                            solara.HTML(
                                tag="div",
                                unsafe_innerHTML=render_snapshot_placeholder(),
                            )
                        else:
                            crowded = top_crowded_pois(model_state.value, POIS, 6)
                            solara.HTML(
                                tag="div",
                                unsafe_innerHTML=render_crowded_section(crowded),
                            )

                        cmp = compare_strategies_for_tourist(
                            you_tourist,
                            POIS,
                            crowding,
                            "popularity",
                            _current_strategy_id(),
                            top_k=3,
                        )
                        cur_id = _current_strategy_id()
                        solara.HTML(
                            tag="div",
                            unsafe_innerHTML=render_strategy_compare(
                                cmp["popularity"],
                                cmp[cur_id],
                                STRATEGY_LABELS.get(cur_id, "Current strategy"),
                            ),
                        )

                solara.HTML(
                    tag="div",
                    classes=["footer-note"],
                    unsafe_innerHTML=(
                        f"Steps: <strong>{step_count.value}</strong> · "
                        f"Strategy: <strong>{strategy_label_state.value}</strong> · "
                        f"72 POIs from Open Data BCN"
                    ),
                )
