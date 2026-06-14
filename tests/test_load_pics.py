"""Tests for PICS CSV loading."""

from pathlib import Path

import pytest

from src.data.load_pics import load_pics_csv, parse_prices_from_timetable

ROOT = Path(__file__).resolve().parents[1]
CSV_PATH = ROOT / "data" / "raw" / "opendatabcn_pics-csv.csv"


@pytest.fixture(scope="module")
def raw_df():
    if not CSV_PATH.exists():
        pytest.skip("Raw CSV not available")
    return load_pics_csv(CSV_PATH)


def test_loads_csv(raw_df):
    assert len(raw_df) >= 800
    assert "name" in raw_df.columns
    assert "geo_epgs_4326_lat" in raw_df.columns


def test_finds_sagrada_familia(raw_df):
    matches = raw_df[raw_df["name"].str.contains("Sagrada Família", na=False)]
    assert len(matches) >= 1


def test_parse_prices():
    html = '<div>Entrada general: 14 € <p>Grups: 8 €</p></div>'
    assert parse_prices_from_timetable(html) == 14.0


def test_parse_free():
    html = "<div>Entrada Gratuïta</div>"
    assert parse_prices_from_timetable(html) == 0.0
