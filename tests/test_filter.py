"""Tests for POI filtering."""

from pathlib import Path

import pytest

from src.data.filter_pois import filter_tourism_pois
from src.data.load_pics import load_pics_csv

ROOT = Path(__file__).resolve().parents[1]
CSV_PATH = ROOT / "data" / "raw" / "opendatabcn_pics-csv.csv"


@pytest.fixture(scope="module")
def filtered_df():
    if not CSV_PATH.exists():
        pytest.skip("Raw CSV not available")
    raw = load_pics_csv(CSV_PATH)
    return filter_tourism_pois(raw)


def test_excludes_centre_civic(filtered_df):
    civic = filtered_df[filtered_df["name"].str.contains("Centre Cívic", na=False)]
    assert len(civic) == 0


def test_keeps_museums(filtered_df):
    museums = filtered_df[filtered_df["name"].str.contains("Museu", na=False)]
    assert len(museums) >= 5


def test_poi_count_in_range(filtered_df):
    assert 55 <= len(filtered_df) <= 85
