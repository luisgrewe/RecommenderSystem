# Data Sources

Provenance registry for the Barcelona sustainable tourism ABM evaluation.

## 1. Cultural interest points (primary POI dataset)

| Field | Value |
|---|---|
| **Local file** | `data/raw/opendatabcn_pics-csv.csv` |
| **Portal** | [Cultural interest points — Open Data BCN (EN)](https://opendata-ajuntament.barcelona.cat/data/en/dataset/punts-informacio-turistica) |
| **Publisher** | Ajuntament de Barcelona — Base de dades centralitzada de Turisme |
| **License** | [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) |
| **Format** | CSV (UTF-16 with BOM) |
| **Records** | 879 unique POIs |
| **Used for** | POI names, coordinates, districts/neighborhoods, `values_outstanding`, price hints in `timetable` |

> Ajuntament de Barcelona. *Punts d'interès cultural de la ciutat de Barcelona*. Open Data BCN.  
> https://opendata-ajuntament.barcelona.cat/data/en/dataset/punts-informacio-turistica

## 2. Tourism intensity by city area (crowding calibration)

| Field | Value |
|---|---|
| **Local file** | `data/raw/intensitat-activitat-turistica/2019_turisme_allotjament.gpkg` |
| **Portal** | [Areas with higher concentration of tourism](https://opendata-ajuntament.barcelona.cat/data/en/dataset/intensitat-activitat-turistica) |
| **Publisher** | Ajuntament de Barcelona — Resiliència Urbana |
| **License** | CC BY 4.0 |
| **Year** | 2019 (accommodation layer) |
| **Used for** | `baseline_tourism_intensity` per POI via spatial join on lat/lon |

> Ajuntament de Barcelona. *Areas of the city of Barcelona with higher concentration of tourism*. Open Data BCN.  
> https://opendata-ajuntament.barcelona.cat/data/en/dataset/intensitat-activitat-turistica

### Data fusion note

POI locations come from the current Open Data BCN catalogue. Tourism intensity comes from the **2019 accommodation layer**. These sources were not collected in the same year. We use intensity as a **relative spatial prior** for initial crowding calibration, not as a contemporaneous visitor count. Simulation dynamics (daily visits, crowding accumulation) are entirely synthetic.

## 3. Enrichment (simulation assumptions — not official open data)

| File | Purpose |
|---|---|
| `data/enrichment/hotspot_rankings.yaml` | Manual top hotspot popularity seed |
| `data/enrichment/manual_pois.yaml` | Seminar POIs missing from PICS |
| `data/enrichment/poi_overrides.yaml` | Per-POI tag/capacity/sustainability overrides |

These files are documented assumptions for the recommender evaluation, not sourced from Open Data BCN.
