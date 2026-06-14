"""Load and merge scenario presets onto base simulation config."""

from __future__ import annotations

from copy import deepcopy
from pathlib import Path
from typing import Any

import yaml

from src.config import DEFAULT_CONFIG_PATH, load_config

DEFAULT_SCENARIOS_PATH = Path(__file__).resolve().parents[1] / "config" / "scenarios.yaml"


def _deep_merge(base: dict[str, Any], overrides: dict[str, Any]) -> dict[str, Any]:
    """Recursively merge overrides into base (overrides win)."""
    merged = deepcopy(base)
    for key, value in overrides.items():
        if key in merged and isinstance(merged[key], dict) and isinstance(value, dict):
            merged[key] = _deep_merge(merged[key], value)
        else:
            merged[key] = deepcopy(value)
    return merged


def load_scenarios(path: str | Path | None = None) -> dict[str, Any]:
    scenarios_path = Path(path) if path else DEFAULT_SCENARIOS_PATH
    with scenarios_path.open(encoding="utf-8") as handle:
        data = yaml.safe_load(handle)
    return data.get("scenarios", {})


def list_scenarios(path: str | Path | None = None) -> list[tuple[str, str]]:
    """Return (name, description) pairs for all scenarios."""
    scenarios = load_scenarios(path)
    return [(name, spec.get("description", "")) for name, spec in scenarios.items()]


def get_scenario(
    name: str,
    *,
    base_config_path: str | Path | None = None,
    scenarios_path: str | Path | None = None,
) -> dict[str, Any]:
    """Merge scenario overrides onto base simulation.yaml config."""
    scenarios = load_scenarios(scenarios_path)
    if name not in scenarios:
        available = ", ".join(sorted(scenarios))
        raise KeyError(f"Unknown scenario '{name}'. Available: {available}")

    base = load_config(base_config_path or DEFAULT_CONFIG_PATH)
    spec = scenarios[name]

    overrides: dict[str, Any] = {}
    for section in ("simulation", "crowding", "recommenders", "batch", "sustainability_weights", "paths"):
        if section in spec:
            overrides[section] = spec[section]

    merged = _deep_merge(base, overrides)
    merged["scenario_name"] = name
    merged["scenario_description"] = spec.get("description", "")
    merged["scenario_help"] = spec.get("help", "")
    merged["tourist_profile"] = deepcopy(spec.get("tourist_profile", {}))
    return merged
