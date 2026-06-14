"""Load Open Data BCN cultural POIs CSV (UTF-16)."""

from __future__ import annotations

import re
from pathlib import Path

import pandas as pd

PRICE_PATTERN = re.compile(
    r"(?:Entrada general(?: de)?(?:\s*:)?|general(?:\s*:)?)\s*(\d+(?:[.,]\d+)?)\s*€",
    re.IGNORECASE,
)
ANY_EURO_PATTERN = re.compile(r"(\d+(?:[.,]\d+)?)\s*€")


def parse_prices_from_timetable(html: str | float | None) -> float | None:
    """Extract a representative EUR price from timetable HTML."""
    if html is None or (isinstance(html, float) and pd.isna(html)):
        return None
    text = str(html)
    if "Gratuïta" in text or "gratuït" in text.lower():
        # Still check for paid tiers below free tier
        pass

    matches = PRICE_PATTERN.findall(text)
    if not matches:
        matches = ANY_EURO_PATTERN.findall(text)
    if not matches:
        if "Gratuïta" in text or "gratuït" in text.lower():
            return 0.0
        return None

    values = [float(m.replace(",", ".")) for m in matches]
    return max(values)


def load_pics_csv(path: str | Path) -> pd.DataFrame:
    """Read UTF-16 CSV and derive price_eur from timetable HTML."""
    df = pd.read_csv(path, encoding="utf-16", dtype=str)
    df["price_eur"] = df.get("timetable", pd.Series(dtype=str)).map(parse_prices_from_timetable)
    df["geo_epgs_4326_lat"] = pd.to_numeric(df["geo_epgs_4326_lat"], errors="coerce")
    df["geo_epgs_4326_lon"] = pd.to_numeric(df["geo_epgs_4326_lon"], errors="coerce")
    df["values_outstanding"] = df.get("values_outstanding", "").astype(str).str.lower() == "true"
    return df
