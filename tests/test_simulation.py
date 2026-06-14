"""Tests for tourism ABM day limits."""

from src.models import POI, Tourist
from src.recommenders.registry import get_strategy
from src.simulation.model import TourismModel


def _minimal_model(num_days: int = 2) -> TourismModel:
    pois = [
        POI(poi_id="p1", name="POI A", lat=41.39, lon=2.17, interest_tags=frozenset({"museum"})),
        POI(poi_id="p2", name="POI B", lat=41.38, lon=2.16, interest_tags=frozenset({"park"})),
    ]
    tourists = [
        Tourist(
            tourist_id="t0",
            interest_tags=frozenset({"museum"}),
            max_price_eur=20.0,
            travel_budget_km=8.0,
            lat=41.387,
            lon=2.173,
        )
    ]
    return TourismModel(
        pois=pois,
        tourists=tourists,
        strategy=get_strategy("popularity"),
        num_days=num_days,
        daily_pois_per_tourist=1,
        seed=42,
    )


def test_simulation_stops_after_num_days():
    model = _minimal_model(num_days=2)
    model.run()
    assert model.is_complete
    visits_after_run = sum(model.total_visits.values())

    model.step()
    model.end_of_day()
    assert sum(model.total_visits.values()) == visits_after_run
