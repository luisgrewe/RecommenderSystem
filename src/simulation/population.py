"""Tourist population spawning from scenario profiles."""

from __future__ import annotations

import random
from typing import Any

from src.models import POI, Tourist

OUTDOOR_TAGS = frozenset({"park", "beach", "nature", "sport", "viewpoint"})
WALKING_TOLERANCE_CHOICES = ("low", "medium", "high")


def _sample_float(rng: random.Random, spec: dict[str, Any]) -> float:
    dist_type = spec.get("type", "uniform")
    if dist_type == "uniform":
        return rng.uniform(spec["min"], spec["max"])
    if dist_type == "normal":
        value = rng.gauss(spec["mean"], spec["std"])
        clip = spec.get("clip")
        if clip:
            value = max(clip[0], min(clip[1], value))
        return value
    if dist_type == "fixed":
        return float(spec["value"])
    raise ValueError(f"Unknown distribution type: {dist_type}")


def _sample_bool(rng: random.Random, spec: dict[str, Any] | float | bool) -> bool:
    if isinstance(spec, bool):
        return spec
    if isinstance(spec, (int, float)):
        return bool(spec)
    return rng.random() < spec.get("probability", 0.5)


def _sample_walking_tolerance(rng: random.Random, spec: str | dict[str, Any] | None) -> str:
    if spec is None:
        return rng.choice(WALKING_TOLERANCE_CHOICES)
    if isinstance(spec, str):
        return spec
    choices = spec.get("choices", list(WALKING_TOLERANCE_CHOICES))
    weights = spec.get("weights")
    if weights:
        return rng.choices(choices, weights=weights, k=1)[0]
    return rng.choice(choices)


def _sample_interest_tags(
    rng: random.Random,
    all_tags: list[str],
    tag_spec: dict[str, Any],
    *,
    prefers_outdoor: bool,
) -> frozenset[str]:
    tag_type = tag_spec.get("type", "random")
    min_tags = tag_spec.get("min_tags", 1)
    max_tags = tag_spec.get("max_tags", 3)
    k = rng.randint(min_tags, max_tags)

    if tag_type == "fixed":
        return frozenset(tag_spec.get("tags", []))

    if tag_type == "weighted_outdoor":
        outdoor_tags = [t for t in tag_spec.get("outdoor_tags", OUTDOOR_TAGS) if t in all_tags]
        other_tags = [t for t in all_tags if t not in outdoor_tags]
        outdoor_weight = tag_spec.get("outdoor_weight", 0.6)
        pool = outdoor_tags if (prefers_outdoor or rng.random() < outdoor_weight) else other_tags
        if not pool:
            pool = all_tags
        k = min(k, len(pool))
        return frozenset(rng.sample(pool, k=k))

    if tag_type == "weighted":
        weights_map: dict[str, float] = tag_spec.get("weights", {})
        weighted_tags = [t for t in all_tags if t in weights_map]
        if not weighted_tags:
            weighted_tags = all_tags
        tag_weights = [weights_map.get(t, 0.1) for t in weighted_tags]
        chosen: set[str] = set()
        for _ in range(min(k, len(weighted_tags))):
            pick = rng.choices(weighted_tags, weights=tag_weights, k=1)[0]
            chosen.add(pick)
        return frozenset(chosen)

    k = min(k, len(all_tags))
    if prefers_outdoor:
        outdoor = [t for t in all_tags if t in OUTDOOR_TAGS]
        if outdoor and rng.random() < 0.7:
            n_outdoor = min(k, max(1, rng.randint(1, k)))
            tags = set(rng.sample(outdoor, k=min(n_outdoor, len(outdoor))))
            remaining = [t for t in all_tags if t not in tags]
            if len(tags) < k and remaining:
                tags.update(rng.sample(remaining, k=min(k - len(tags), len(remaining))))
            return frozenset(tags)

    return frozenset(rng.sample(all_tags, k=k))


def _spawn_fixed_tourist(pois: list[POI], cfg: dict[str, Any], profile: dict[str, Any]) -> list[Tourist]:
    sim = cfg["simulation"]
    if pois:
        center_lat = sum(p.lat for p in pois) / len(pois)
        center_lon = sum(p.lon for p in pois) / len(pois)
    else:
        center_lat = 41.387
        center_lon = 2.173

    tags = profile.get("interest_tags", [])
    if isinstance(tags, list):
        interest_tags = frozenset(tags)
    else:
        interest_tags = frozenset()

    return [
        Tourist(
            tourist_id=profile.get("tourist_id", "case_study_01"),
            interest_tags=interest_tags,
            max_price_eur=profile.get("max_price_eur") or sim["max_price_eur"],
            travel_budget_km=profile.get("travel_budget_km") or sim["travel_budget_km"],
            lat=profile.get("lat", center_lat),
            lon=profile.get("lon", center_lon),
            crowd_aversion=float(profile.get("crowd_aversion", 0.3)),
            sustainability_sensitivity=float(profile.get("sustainability_sensitivity", 0.5)),
            prefers_outdoor=bool(profile.get("prefers_outdoor", False)),
            travel_with_kids=bool(profile.get("travel_with_kids", False)),
            trip_pace=str(profile.get("trip_pace", "standard")),
            group_type=str(profile.get("group_type", "solo")),
            walking_tolerance=str(profile.get("walking_tolerance", "medium")),
        )
    ]


def spawn_tourists(
    pois: list[POI],
    cfg: dict[str, Any],
    scenario: str | None = None,
    seed: int = 42,
) -> list[Tourist]:
    """Spawn tourists using scenario tourist_profile distributions."""
    rng = random.Random(seed)
    sim = cfg["simulation"]
    profile = cfg.get("tourist_profile", {})
    mode = profile.get("mode", "population")

    if mode == "fixed":
        return _spawn_fixed_tourist(pois, cfg, profile)

    all_tags = sorted({tag for p in pois for tag in p.interest_tags})
    center_lat = sum(p.lat for p in pois) / len(pois)
    center_lon = sum(p.lon for p in pois) / len(pois)

    tag_spec = profile.get("interest_tags", {"type": "random", "min_tags": 1, "max_tags": 3})
    tourists: list[Tourist] = []

    for i in range(sim["num_tourists"]):
        prefers_outdoor = _sample_bool(rng, profile.get("prefers_outdoor", False))
        travel_with_kids = _sample_bool(rng, profile.get("travel_with_kids", False))

        tags = _sample_interest_tags(rng, all_tags, tag_spec, prefers_outdoor=prefers_outdoor)

        max_price = profile.get("max_price_eur", sim["max_price_eur"])
        budget_spec = profile.get("travel_budget_km_multiplier", {"min": 0.7, "max": 1.0})
        if isinstance(budget_spec, dict):
            travel_budget = sim["travel_budget_km"] * rng.uniform(budget_spec["min"], budget_spec["max"])
        else:
            travel_budget = sim["travel_budget_km"] * float(budget_spec)

        crowd_spec = profile.get("crowd_aversion", {"type": "uniform", "min": 0.2, "max": 0.4})
        if isinstance(crowd_spec, (int, float)):
            crowd_aversion = float(crowd_spec)
        else:
            crowd_aversion = _sample_float(rng, crowd_spec)

        sus_spec = profile.get(
            "sustainability_sensitivity",
            {"type": "uniform", "min": 0.4, "max": 0.6},
        )
        if isinstance(sus_spec, (int, float)):
            sustainability_sensitivity = float(sus_spec)
        else:
            sustainability_sensitivity = _sample_float(rng, sus_spec)

        walking_tolerance = _sample_walking_tolerance(rng, profile.get("walking_tolerance"))

        if travel_with_kids:
            group_type = "family"
        else:
            group_type = rng.choices(
                ["solo", "couple", "group"],
                weights=[0.45, 0.4, 0.15],
                k=1,
            )[0]
        trip_pace = rng.choices(
            ["relaxed", "standard", "packed"],
            weights=[0.25, 0.5, 0.25],
            k=1,
        )[0]

        tourists.append(
            Tourist(
                tourist_id=f"t_{i}",
                interest_tags=tags,
                max_price_eur=max_price,
                travel_budget_km=travel_budget,
                lat=center_lat + rng.uniform(-0.02, 0.02),
                lon=center_lon + rng.uniform(-0.02, 0.02),
                crowd_aversion=crowd_aversion,
                sustainability_sensitivity=sustainability_sensitivity,
                prefers_outdoor=prefers_outdoor,
                travel_with_kids=travel_with_kids,
                trip_pace=trip_pace,
                group_type=group_type,
                walking_tolerance=walking_tolerance,
            )
        )
    return tourists
