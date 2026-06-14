#!/usr/bin/env python3
"""Build processed POI dataset from raw Open Data BCN sources."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.data.pipeline import run_pipeline  # noqa: E402


def main() -> None:
    df, pois = run_pipeline()
    print(f"Built {len(pois)} POIs -> data/processed/pois_simulation.csv")
    print(f"Columns: {', '.join(df.columns[:8])}...")


if __name__ == "__main__":
    main()
