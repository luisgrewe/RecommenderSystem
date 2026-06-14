"""Tourist agents for the Mesa ABM."""

from __future__ import annotations

from typing import TYPE_CHECKING

from mesa import Agent

from src.models import POI, Tourist
from src.recommenders.base import RecommenderStrategy
from src.recommenders.trip_profile import accept_steepness_for, effective_crowd_aversion
from src.simulation.visit_logic import accept_probability

if TYPE_CHECKING:
    from src.simulation.model import TourismModel


class TouristAgent(Agent):
    """Tourist that receives recommendations and forms trip chains."""

    def __init__(
        self,
        model: TourismModel,
        tourist: Tourist,
        strategy: RecommenderStrategy,
    ) -> None:
        super().__init__(model)
        self.tourist = tourist
        self.strategy = strategy
        self.current_lat = tourist.lat
        self.current_lon = tourist.lon
        self.visits: list[str] = []
        self.accepted_today = 0

    def reset_daily(self) -> None:
        self.accepted_today = 0

    def step(self) -> None:
        if self.accepted_today >= self.model.daily_pois_per_tourist:
            return

        tourist_snapshot = Tourist(
            tourist_id=self.tourist.tourist_id,
            interest_tags=self.tourist.interest_tags,
            max_price_eur=self.tourist.max_price_eur,
            travel_budget_km=self.tourist.travel_budget_km,
            lat=self.current_lat,
            lon=self.current_lon,
            crowd_aversion=self.tourist.crowd_aversion,
            sustainability_sensitivity=self.tourist.sustainability_sensitivity,
            prefers_outdoor=self.tourist.prefers_outdoor,
            travel_with_kids=self.tourist.travel_with_kids,
            trip_pace=self.tourist.trip_pace,
            group_type=self.tourist.group_type,
            walking_tolerance=self.tourist.walking_tolerance,
        )
        recs = self.strategy.recommend(
            tourist_snapshot,
            self.model.pois,
            self.model.crowding,
            top_k=self.model.top_k,
        )
        if not recs:
            return

        for rec in recs:
            if self.accepted_today >= self.model.daily_pois_per_tourist:
                break
            if rec.poi.poi_id in self.visits[-3:]:
                continue

            state = self.model.crowding[rec.poi.poi_id]
            prob = accept_probability(
                rec.score,
                state,
                soft_threshold=self.model.soft_threshold,
                steepness=accept_steepness_for(
                    self.tourist, self.model.accept_steepness
                ),
                crowd_aversion=effective_crowd_aversion(self.tourist),
            )
            if self.random.random() <= prob:
                self._visit(rec.poi)
                break

    def _visit(self, poi: POI) -> None:
        self.model.record_visit(poi.poi_id)
        self.visits.append(poi.poi_id)
        self.accepted_today += 1
        self.current_lat = poi.lat
        self.current_lon = poi.lon
