"""Spatial join POI coordinates to tourism intensity polygons."""

from __future__ import annotations

from pathlib import Path

import geopandas as gpd
import pandas as pd
from shapely.geometry import Point


def attach_baseline_intensity(
    df: pd.DataFrame,
    gpkg_path: str | Path,
    lat_col: str = "geo_epgs_4326_lat",
    lon_col: str = "geo_epgs_4326_lon",
) -> pd.DataFrame:
    """Join each POI to the 2019 accommodation intensity layer (DN field)."""
    gdf_poly = gpd.read_file(gpkg_path)
    if "DN" not in gdf_poly.columns:
        raise ValueError(f"Expected DN column in {gpkg_path}, got {gdf_poly.columns.tolist()}")

    geometry = [Point(lon, lat) for lon, lat in zip(df[lon_col], df[lat_col], strict=True)]
    gdf_poi = gpd.GeoDataFrame(df.copy(), geometry=geometry, crs="EPSG:4326")
    gdf_poly = gdf_poly.to_crs("EPSG:4326")

    joined = gpd.sjoin(gdf_poi, gdf_poly[["DN", "geometry"]], how="left", predicate="within")
    dn = joined["DN"].fillna(joined["DN"].median())
    dn_min, dn_max = dn.min(), dn.max()
    if dn_max > dn_min:
        normalized = (dn - dn_min) / (dn_max - dn_min)
    else:
        normalized = pd.Series(0.5, index=joined.index)

    result = joined.drop(columns=["index_right", "geometry"], errors="ignore")
    result["baseline_tourism_intensity"] = normalized.astype(float)
    return pd.DataFrame(result)
