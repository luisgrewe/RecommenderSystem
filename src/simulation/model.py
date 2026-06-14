"""Mesa tourism ABM with POI crowding and trip chains."""

from __future__ import annotations

from typing import Any
from mesa import Model
from mesa.datacollection import DataCollector

from src.models import CrowdingState, POI, Tourist
from src.recommenders.base import RecommenderStrategy
from src.simulation.agents import TouristAgent


def simulation_complete(model: TourismModel) -> bool:
    """True when all configured days have finished (safe for hot-reload)."""
    return model.current_day > model.num_days


class TourismModel(Model):
    """Daily loop ABM: recommend -> accept -> visit -> update crowding."""

    def __init__(
        self,
        pois: list[POI],
        tourists: list[Tourist],
        strategy: RecommenderStrategy,
        *,
        num_days: int = 5,
        daily_pois_per_tourist: int = 2,
        soft_threshold: float = 0.6,
        accept_steepness: float = 4.0,
        decay_rate: float = 0.15,
        top_k: int = 5,
        seed: int = 42,
        initial_load_boost: float = 0.0,
    ) -> None:
        super().__init__(seed=seed)
        self.pois = pois
        self.poi_by_id = {p.poi_id: p for p in pois}
        self.strategy = strategy
        self.num_days = num_days
        self.current_day = 1
        self.daily_pois_per_tourist = daily_pois_per_tourist
        self.soft_threshold = soft_threshold
        self.accept_steepness = accept_steepness
        self.decay_rate = decay_rate
        self.top_k = top_k

        self.crowding: dict[str, CrowdingState] = {}
        for p in pois:
            state = CrowdingState(
                poi_id=p.poi_id,
                capacity=p.capacity,
                baseline_intensity=p.baseline_tourism_intensity,
            )
            if initial_load_boost > 0:
                state.visits_today = int(p.capacity * initial_load_boost * p.baseline_tourism_intensity)
            self.crowding[p.poi_id] = state
        self.total_visits: dict[str, int] = {p.poi_id: 0 for p in pois}
        self.daily_visit_log: list[dict[str, Any]] = []

        self.datacollector = DataCollector(
            agent_reporters={
                "visits_count": lambda a: len(a.visits),
                "accepted_today": lambda a: a.accepted_today,
            },
            model_reporters={
                "day": lambda m: m.current_day,
                "total_visits": lambda m: sum(m.total_visits.values()),
                "mean_crowding": lambda m: sum(s.combined_crowding for s in m.crowding.values())
                / max(1, len(m.crowding)),
            },
        )

        self.tourist_profiles = tourists
        for tourist in tourists:
            TouristAgent(self, tourist, strategy)

    @property
    def is_complete(self) -> bool:
        return simulation_complete(self)

    def record_visit(self, poi_id: str) -> None:
        self.crowding[poi_id].visits_today += 1
        self.total_visits[poi_id] += 1

    def end_of_day(self) -> None:
        if simulation_complete(self):
            return
        visit_counts = {pid: state.visits_today for pid, state in self.crowding.items()}
        self.daily_visit_log.append({"day": self.current_day, **visit_counts})

        for state in self.crowding.values():
            state.visits_today = max(0, int(state.visits_today * (1.0 - self.decay_rate)))

        for agent in self.agents:
            agent.reset_daily()

        self.current_day += 1

    def step(self) -> None:
        if simulation_complete(self):
            return
        self.datacollector.collect(self)
        self.agents.shuffle_do("step")

    def run(self) -> dict[str, Any]:
        for _ in range(self.num_days):
            for _ in range(self.daily_pois_per_tourist):
                self.step()
            self.end_of_day()
        return {
            "total_visits": dict(self.total_visits),
            "daily_log": self.daily_visit_log,
        }
