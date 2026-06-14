"""Orchestrate POI data pipeline."""

from __future__ import annotations

from pathlib import Path

import pandas as pd

from src.config import load_config
from src.data.enrich_pois import dataframe_to_pois, enrich_pois
from src.data.filter_pois import filter_tourism_pois
from src.data.intensity import attach_baseline_intensity
from src.data.load_pics import load_pics_csv
from src.data.tagging import add_interest_tags
from src.models import POI


def build_poi_dataframe(config: dict | None = None) -> pd.DataFrame:
    cfg = config or load_config()
    paths = cfg["paths"]

    raw = load_pics_csv(paths["raw_pics_csv"])
    filtered = filter_tourism_pois(raw)
    tagged = add_interest_tags(filtered)
    with_intensity = attach_baseline_intensity(tagged, paths["intensity_gpkg"])
    enriched = enrich_pois(
        with_intensity,
        paths["hotspot_rankings"],
        paths["manual_pois"],
        paths["poi_overrides"],
    )
    return enriched


def save_processed_pois(df: pd.DataFrame, output_path: str | Path) -> Path:
    out = Path(output_path)
    out.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(out, index=False)
    return out


def load_processed_pois(path: str | Path) -> list[POI]:
    df = pd.read_csv(path)
    return dataframe_to_pois(df)


def run_pipeline(config: dict | None = None) -> tuple[pd.DataFrame, list[POI]]:
    cfg = config or load_config()
    df = build_poi_dataframe(cfg)
    save_processed_pois(df, cfg["paths"]["processed_pois"])
    return df, dataframe_to_pois(df)
