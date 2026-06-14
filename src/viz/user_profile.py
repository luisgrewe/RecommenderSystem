"""Build a Tourist profile from dashboard controls."""

from __future__ import annotations

from dataclasses import dataclass

from src.data.pricing import format_poi_entry_price
from src.models import POI, Tourist
from src.recommenders.trip_profile import GROUP_TYPE_LABELS, TRIP_PACE_LABELS

BARCELONA_CENTER = (41.387, 2.173)

INTEREST_TAG_LABELS: dict[str, str] = {
    "architecture": "Architecture",
    "entertainment": "Entertainment",
    "general": "General sightseeing",
    "history": "History",
    "market": "Markets",
    "museum": "Museums",
    "nature": "Nature",
    "park": "Parks",
    "religious": "Religious sites",
    "sport": "Sport",
    "viewpoint": "Viewpoints",
}

WALKING_TOLERANCE_OPTIONS = ["low", "medium", "high"]

# One control for the dashboard: distance cap + mobility scoring.
TRAVEL_RANGE_OPTIONS = [
    "Limited mobility — up to 2 km per visit",
    "Stay nearby — up to 5 km per visit",
    "Across the city — up to 8 km per visit",
    "Go anywhere — up to 12 km per visit",
]
DEFAULT_TRAVEL_RANGE = TRAVEL_RANGE_OPTIONS[2]

TRAVEL_RANGE_PRESETS: dict[str, tuple[float, str]] = {
    TRAVEL_RANGE_OPTIONS[0]: (2.0, "low"),
    TRAVEL_RANGE_OPTIONS[1]: (5.0, "medium"),
    TRAVEL_RANGE_OPTIONS[2]: (8.0, "medium"),
    TRAVEL_RANGE_OPTIONS[3]: (12.0, "high"),
}


def travel_preset(label: str) -> tuple[float, str]:
    return TRAVEL_RANGE_PRESETS.get(label, (8.0, "medium"))


ENTRY_PRICE_OPTIONS = [
    "Free only",
    "Up to €10 per entry",
    "Up to €20 per entry",
    "Up to €30 per entry",
    "Up to €50 per entry",
    "Any price",
]
DEFAULT_ENTRY_PRICE = ENTRY_PRICE_OPTIONS[4]  # Up to €50 — close to simulation default (€35)

TRIP_PACE_OPTIONS = ["Relaxed", "Standard", "Packed"]
DEFAULT_TRIP_PACE = TRIP_PACE_OPTIONS[1]

GROUP_TYPE_OPTIONS = ["Solo", "Couple", "Family", "Group"]
DEFAULT_GROUP_TYPE = GROUP_TYPE_OPTIONS[0]

TRIP_PACE_IDS: dict[str, str] = {
    TRIP_PACE_OPTIONS[0]: "relaxed",
    TRIP_PACE_OPTIONS[1]: "standard",
    TRIP_PACE_OPTIONS[2]: "packed",
}

GROUP_TYPE_IDS: dict[str, str] = {
    GROUP_TYPE_OPTIONS[0]: "solo",
    GROUP_TYPE_OPTIONS[1]: "couple",
    GROUP_TYPE_OPTIONS[2]: "family",
    GROUP_TYPE_OPTIONS[3]: "group",
}


def trip_pace_id(label: str) -> str:
    return TRIP_PACE_IDS.get(label, "standard")


def group_type_id(label: str) -> str:
    return GROUP_TYPE_IDS.get(label, "solo")

ENTRY_PRICE_PRESETS: dict[str, float] = {
    ENTRY_PRICE_OPTIONS[0]: 0.0,
    ENTRY_PRICE_OPTIONS[1]: 10.0,
    ENTRY_PRICE_OPTIONS[2]: 20.0,
    ENTRY_PRICE_OPTIONS[3]: 30.0,
    ENTRY_PRICE_OPTIONS[4]: 50.0,
    ENTRY_PRICE_OPTIONS[5]: 999.0,
}


def entry_price_preset(label: str) -> float:
    return ENTRY_PRICE_PRESETS.get(label, 50.0)


def format_entry_price_cap(max_price_eur: float) -> str:
    if max_price_eur <= 0:
        return "Free only"
    if max_price_eur >= 999:
        return "Any price"
    return f"Up to €{max_price_eur:.0f} per entry"


@dataclass(frozen=True)
class ViewerTrip:
    """Dashboard user profile — separate from ABM simulation tourists."""

    tourist: Tourist
    must_visit_poi_ids: frozenset[str] = frozenset()
    trip_pace: str = "standard"
    group_type: str = "solo"


def tourist_for_recommendations(trip: ViewerTrip) -> Tourist:
    """Attach trip pace/group for scoring (Solara-safe)."""
    from src.recommenders.trip_profile import attach_trip_context

    return attach_trip_context(
        trip.tourist,
        trip_pace=trip.trip_pace,
        group_type=trip.group_type,
    )


def available_interest_tags(pois: list[POI]) -> list[str]:
    return sorted({tag for p in pois for tag in p.interest_tags})


def interest_tag_labels(pois: list[POI]) -> list[str]:
    tags = available_interest_tags(pois)
    return [INTEREST_TAG_LABELS.get(t, t.title()) for t in tags]


def label_to_interest_tag(label: str, pois: list[POI]) -> str:
    for tag in available_interest_tags(pois):
        if INTEREST_TAG_LABELS.get(tag, tag.title()) == label:
            return tag
    return label.lower()


def poi_display_label(poi: POI) -> str:
    district = poi.district or "Barcelona"
    name = poi.name if len(poi.name) <= 48 else poi.name[:45] + "..."
    price = format_poi_entry_price(poi)
    return f"{name} ({district}, {price})"


def poi_choices(pois: list[POI]) -> tuple[list[str], dict[str, str]]:
    """Return sorted display labels and label -> poi_id mapping."""
    ranked = sorted(pois, key=lambda p: (-p.popularity_score, p.name.lower()))
    labels = [poi_display_label(p) for p in ranked]
    label_to_id = {poi_display_label(p): p.poi_id for p in ranked}
    return labels, label_to_id


def build_viewer_trip(
    *,
    interest_labels: list[str],
    entry_price_label: str,
    travel_range_label: str,
    trip_pace_label: str,
    group_type_label: str,
    crowd_aversion: float,
    sustainability_sensitivity: float,
    must_visit_labels: list[str],
    pois: list[POI],
    label_to_poi_id: dict[str, str],
) -> ViewerTrip:
    tags = frozenset(label_to_interest_tag(l, pois) for l in interest_labels)
    must_visit = frozenset(
        label_to_poi_id[l] for l in must_visit_labels if l in label_to_poi_id
    )
    travel_budget_km, walking_tolerance = travel_preset(travel_range_label)
    max_price_eur = entry_price_preset(entry_price_label)
    lat, lon = BARCELONA_CENTER
    tourist = Tourist(
        tourist_id="you",
        interest_tags=tags,
        max_price_eur=max_price_eur,
        travel_budget_km=travel_budget_km,
        lat=lat,
        lon=lon,
        crowd_aversion=crowd_aversion,
        sustainability_sensitivity=sustainability_sensitivity,
        walking_tolerance=walking_tolerance,
    )
    return ViewerTrip(
        tourist=tourist,
        must_visit_poi_ids=must_visit,
        trip_pace=trip_pace_id(trip_pace_label),
        group_type=group_type_id(group_type_label),
    )


def profile_summary(trip: ViewerTrip, pois: list[POI]) -> str:
    tourist = trip.tourist
    tags = ", ".join(
        INTEREST_TAG_LABELS.get(t, t.title()) for t in sorted(tourist.interest_tags)
    ) or "—"
    extras: list[str] = []
    if trip.must_visit_poi_ids:
        poi_by_id = {p.poi_id: p for p in pois}
        names = [
            poi_by_id[pid].name[:30]
            for pid in sorted(trip.must_visit_poi_ids)
            if pid in poi_by_id
        ]
        extras.append(f"must visit: {', '.join(names)}")
    extra_text = f" · {' · '.join(extras)}" if extras else ""
    return (
        f"Interests: {tags} · {format_entry_price_cap(tourist.max_price_eur)} · "
        f"Up to {tourist.travel_budget_km:.0f} km per visit · "
        f"Pace {TRIP_PACE_LABELS.get(trip.trip_pace, trip.trip_pace)} · "
        f"{GROUP_TYPE_LABELS.get(trip.group_type, trip.group_type)} · "
        f"Crowd aversion {tourist.crowd_aversion:.0%} · "
        f"Sustainability focus {tourist.sustainability_sensitivity:.0%}{extra_text}"
    )
