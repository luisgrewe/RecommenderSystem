"""Human-readable POI entry price labels and free-entry heuristics."""

from __future__ import annotations

from src.models import POI

FREE_ENTRY_TAGS = frozenset({"park", "nature", "religious"})
PAID_LIKELY_TAGS = frozenset({"museum", "sport", "entertainment"})


def format_poi_entry_price(poi: POI) -> str:
    """Short label for UI lists — avoids '?' when source data has no ticket price."""
    if poi.price_eur == 0:
        return "Free entry"
    if poi.price_eur is not None and poi.price_eur > 0:
        return f"€{poi.price_eur:.0f} entry"

    tags = poi.interest_tags
    if "market" in tags:
        return "Free entry · pay at stalls"
    if tags & FREE_ENTRY_TAGS:
        return "Free entry"
    if tags & PAID_LIKELY_TAGS:
        return "Paid entry · price varies"
    return "No fixed entry fee"


def entry_price_for_card(poi: POI) -> str:
    """Compact entry price for recommendation cards."""
    from src.viz.rec_format import entry_price_for_card as _card

    return _card(poi)


def is_free_entry_poi(poi: POI) -> bool:
    """True when entry is free or very likely free (used for recommendation hints)."""
    if poi.price_eur == 0:
        return True
    if poi.price_eur is not None:
        return False
    tags = poi.interest_tags
    return "market" in tags or bool(tags & FREE_ENTRY_TAGS)
