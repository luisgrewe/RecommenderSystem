"""Tests for POI entry price display helpers."""

from src.data.pricing import entry_price_for_card, format_poi_entry_price, is_free_entry_poi
from src.models import POI
from src.viz.rec_format import ENTRY_FREE, ENTRY_FREE_STALLS, ENTRY_PAID_VARIES


def test_market_unknown_price_shows_stalls_label():
    poi = POI(
        poi_id="m1",
        name="Mercat Boqueria",
        lat=41.38,
        lon=2.17,
        price_eur=None,
        interest_tags=frozenset({"market", "history"}),
    )
    assert format_poi_entry_price(poi) == "Free entry · pay at stalls"
    assert is_free_entry_poi(poi)


def test_paid_unknown_museum_shows_varies():
    poi = POI(
        poi_id="m2",
        name="Some Museum",
        lat=41.38,
        lon=2.17,
        price_eur=None,
        interest_tags=frozenset({"museum"}),
    )
    assert format_poi_entry_price(poi) == "Paid entry · price varies"
    assert not is_free_entry_poi(poi)


def test_zero_price_shows_free_entry():
    poi = POI(
        poi_id="p1",
        name="Park",
        lat=41.38,
        lon=2.17,
        price_eur=0.0,
        interest_tags=frozenset({"park"}),
    )
    assert format_poi_entry_price(poi) == "Free entry"
    assert entry_price_for_card(poi) == ENTRY_FREE


def test_card_labels_are_short_and_consistent():
    free = POI("p2", "Basilica", 41.39, 2.17, price_eur=None, interest_tags=frozenset({"religious"}))
    paid = POI("p3", "Camp Nou", 41.39, 2.17, price_eur=None, interest_tags=frozenset({"sport"}))
    market = POI("p4", "Boqueria", 41.39, 2.17, price_eur=None, interest_tags=frozenset({"market"}))
    ticket = POI("p5", "Museum", 41.39, 2.17, price_eur=12.0, interest_tags=frozenset({"museum"}))

    assert entry_price_for_card(free) == ENTRY_FREE
    assert entry_price_for_card(paid) == ENTRY_PAID_VARIES
    assert entry_price_for_card(market) == ENTRY_FREE_STALLS
    assert entry_price_for_card(ticket) == "€12"
    assert " entry" not in entry_price_for_card(free).lower()
    assert " entry" not in entry_price_for_card(paid).lower()
