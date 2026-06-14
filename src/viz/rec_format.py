"""Recommendation card formatting (viz layer)."""

from __future__ import annotations

from src.models import POI

FREE_ENTRY_TAGS = frozenset({"park", "nature", "religious"})
PAID_LIKELY_TAGS = frozenset({"museum", "sport", "entertainment"})

# Short labels for "Entry …" lines on recommendation cards (no repeated "entry").
ENTRY_FREE = "Free"
ENTRY_FREE_STALLS = "Free · pay at stalls"
ENTRY_PAID_VARIES = "Paid · price varies"
ENTRY_NO_FEE = "No fixed fee"


def entry_price_for_card(poi: POI) -> str:
    """Compact, consistent entry price for recommendation card meta lines."""
    if poi.price_eur == 0:
        return ENTRY_FREE
    if poi.price_eur is not None and poi.price_eur > 0:
        return f"€{poi.price_eur:.0f}"

    tags = poi.interest_tags
    if "market" in tags:
        return ENTRY_FREE_STALLS
    if tags & FREE_ENTRY_TAGS:
        return ENTRY_FREE
    if tags & PAID_LIKELY_TAGS:
        return ENTRY_PAID_VARIES
    return ENTRY_NO_FEE


def is_free_entry_poi(poi: POI) -> bool:
    if poi.price_eur == 0:
        return True
    if poi.price_eur is not None:
        return False
    tags = poi.interest_tags
    return "market" in tags or bool(tags & FREE_ENTRY_TAGS)
