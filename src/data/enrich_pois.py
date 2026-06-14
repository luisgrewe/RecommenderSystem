"""Merge enrichment YAML and compute sustainability scores."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import pandas as pd
import yaml

from src.models import POI


def _load_yaml(path: str | Path) -> dict[str, Any]:
    yaml_path = Path(path)
    if not yaml_path.exists():
        return {}
    with yaml_path.open(encoding="utf-8") as handle:
        data = yaml.safe_load(handle)
    return data or {}


def _parse_tags(value: str | list[str] | None) -> frozenset[str]:
    if value is None:
        return frozenset()
    if isinstance(value, list):
        return frozenset(value)
    return frozenset(t.strip() for t in str(value).split("|") if t.strip())


def apply_hotspot_rankings(df: pd.DataFrame, rankings_path: str | Path) -> pd.DataFrame:
    data = _load_yaml(rankings_path)
    hotspots = data.get("hotspots", [])
    result = df.copy()
    result["popularity_score"] = 0.5

    for hotspot in hotspots:
        substring = hotspot["name_substring"]
        score = float(hotspot["popularity_score"])
        mask = result["name"].str.contains(substring, case=False, na=False)
        result.loc[mask, "popularity_score"] = score

    if "values_outstanding" in result.columns:
        outstanding_boost = result["values_outstanding"].astype(bool).map({True: 0.05, False: 0.0})
        result["popularity_score"] = (result["popularity_score"] + outstanding_boost).clip(0, 1)

    return result


def append_manual_pois(df: pd.DataFrame, manual_path: str | Path) -> pd.DataFrame:
    data = _load_yaml(manual_path)
    manual = data.get("pois", [])
    if not manual:
        return df

    rows = []
    for entry in manual:
        rows.append(
            {
                "register_id": entry.get("poi_id", entry["name"][:20].replace(" ", "_")),
                "name": entry["name"],
                "geo_epgs_4326_lat": entry["lat"],
                "geo_epgs_4326_lon": entry["lon"],
                "addresses_district_name": entry.get("district", ""),
                "addresses_neighborhood_name": entry.get("neighborhood", ""),
                "price_eur": entry.get("price_eur"),
                "interest_tags": "|".join(entry.get("interest_tags", [])),
                "popularity_score": entry.get("popularity_score", 0.7),
                "baseline_tourism_intensity": entry.get("baseline_tourism_intensity", 0.5),
                "capacity": entry.get("capacity", 500),
                "values_outstanding": entry.get("outstanding", True),
            }
        )
    manual_df = pd.DataFrame(rows)
    combined = pd.concat([df, manual_df], ignore_index=True)
    combined = combined.drop_duplicates(subset=["name"], keep="first")
    return combined.reset_index(drop=True)


def apply_poi_overrides(df: pd.DataFrame, overrides_path: str | Path) -> pd.DataFrame:
    data = _load_yaml(overrides_path)
    overrides = data.get("overrides", {})
    if not overrides:
        return df

    result = df.copy()
    for name_substring, override in overrides.items():
        mask = result["name"].str.contains(name_substring, case=False, na=False)
        for key, value in override.items():
            if key == "interest_tags" and isinstance(value, list):
                result.loc[mask, "interest_tags"] = "|".join(value)
            else:
                result.loc[mask, key] = value
    return result


def compute_sustainability_rubric(row: pd.Series) -> float:
    """Documented rubric: low intensity + tag diversity + free/affordable access."""
    intensity = float(row.get("baseline_tourism_intensity", 0.5))
    env_score = 1.0 - intensity

    tags = _parse_tags(row.get("interest_tags"))
    culture_tags = {"museum", "history", "religious", "architecture"}
    culture_score = 1.0 if tags & culture_tags else 0.6

    price = row.get("price_eur")
    if price is None or (isinstance(price, float) and pd.isna(price)):
        economy_score = 0.7
    elif float(price) == 0:
        economy_score = 1.0
    elif float(price) <= 10:
        economy_score = 0.85
    elif float(price) <= 20:
        economy_score = 0.65
    else:
        economy_score = 0.4

    return float(0.45 * env_score + 0.35 * culture_score + 0.20 * economy_score)


def enrich_pois(
    df: pd.DataFrame,
    hotspot_rankings_path: str | Path,
    manual_pois_path: str | Path,
    poi_overrides_path: str | Path,
) -> pd.DataFrame:
    result = apply_hotspot_rankings(df, hotspot_rankings_path)
    result = append_manual_pois(result, manual_pois_path)
    result = apply_poi_overrides(result, poi_overrides_path)
    # result["sustainability_score"] = result.apply(compute_sustainability_rubric, axis=1)
    if "capacity" not in result.columns:
        result["capacity"] = 500
    result["capacity"] = result["capacity"].fillna(500).astype(int)
    return result


def dataframe_to_pois(df: pd.DataFrame) -> list[POI]:
    pois: list[POI] = []
    for _, row in df.iterrows():
        price = row.get("price_eur")
        if pd.isna(price):
            price_val = None
        else:
            price_val = float(price)
        pois.append(
            POI(
                poi_id=str(row["register_id"]),
                name=str(row["name"]),
                lat=float(row["geo_epgs_4326_lat"]),
                lon=float(row["geo_epgs_4326_lon"]),
                district=str(row.get("addresses_district_name", "") or ""),
                neighborhood=str(row.get("addresses_neighborhood_name", "") or ""),
                price_eur=price_val,
                interest_tags=_parse_tags(row.get("interest_tags")),
                popularity_score=float(row.get("popularity_score", 0.5)),
                sustainability_score=float(row.get("sustainability_score", 0.5)),
                baseline_tourism_intensity=float(row.get("baseline_tourism_intensity", 0.5)),
                capacity=int(row.get("capacity", 500)),
                outstanding=bool(row.get("values_outstanding", False)),
            )
        )
    return pois
