"""Curate tourism-relevant POIs from the raw PICS catalogue."""

from __future__ import annotations

import pandas as pd

STRONG_KEYWORDS = [
    "museu",
    "museum",
    "basílica",
    "basilica",
    "catedral",
    "cathedral",
    "sagrada família",
    "sagrada familia",
    "park güell",
    "park guell",
    "boqueria",
    "casa batlló",
    "casa batllo",
    "casa milà",
    "casa mila",
    "la pedrera",
    "palau güell",
    "palau guell",
    "casa vicens",
    "casa amatller",
    "casa terradas",
    "punxes",
    "montjuïc",
    "montjuic",
    "castell",
    "castle",
    "cosmocaixa",
    "picasso",
    "camp nou",
    "aquàrium",
    "aquarium",
    "zoo",
    "jardí botànic",
    "jardi botic",
    "funicular",
    "telefèric",
    "teleferic",
    "tibidabo",
    "sagrat cor",
    "memorial",
    "refugi antiaeri",
    "born. museu",
    "història de barcelona",
    "historia de barcelona",
    "història de catalunya",
    "historia de catalunya",
    "monestir",
    "monaster",
    "gaudí",
    "gaudi",
    "modernist",
    "modernista",
    "caixaforum",
    "mnac",
    "macba",
    "fira",
    "fòrum",
    "forum",
]

SECONDARY_KEYWORDS = [
    "església",
    "esglesia",
    "temple",
    "parròquia",
    "parroquia",
    "parc",
    " park",
    "jardí",
    "jardi",
    "mercat",
    "market",
    "palau",
    "palace",
    "platja",
    "beach",
    "mirador",
    "teatre",
    "theatre",
    "auditori",
]

EXCLUDE_KEYWORDS = [
    "centre cívic",
    "centre civic",
    "casal",
    "escola",
    "school",
    "institut",
    "biblioteca",
    "library",
    "oficina",
    "servei",
    "serveis",
    "consultori",
    "residència",
    "residencia",
    "guarderia",
    "llar d'infants",
    "centre d'empreses",
    "centre de formació",
    "centre de formacio",
    "centre de salut",
    "poliesportiu",
    "piscina municipal",
    "mercat de barri",
    "mercat municipal",
    "mercat setmanal",
    "mercadillo",
    "aparcament",
    "parking",
    "estació",
    "estacio",
    "farmàcia",
    "farmacia",
    "ateneu",
    "botiga",
    "bar musical",
    "alberg",
    "cementiri",
    "cementerio",
    "funer",
    "tanatori",
    "casa de barcelona",  # housing blocks named casa X
    "casa rusca",
    "casa bartomeu",
    "casa comalat",
    "casa marsans",
    "casa sant felip",
    "casa de l'aigua",
    "casa del guarda",
    "antiga fàbrica",
    "antiga fabrica",
    "fabricació digital",
    "fabricacio digital",
]

ALLOWLIST_NAMES = [
    "Temple Expiatori del Sagrat Cor",
    "Museu d'Història de Catalunya",
    "Temple Expiatori de la Sagrada Família",
    "Park Güell",
    "Casa Batlló",
    "Mercat Boqueria",
    "Palau Güell",
    "Casa Milà",
    "La Pedrera",
    "Museu Picasso",
    "CosmoCaixa Barcelona",
    "Castell de Montjuïc",
    "El Born. Museu d'Història de Barcelona",
    "Santa Església Catedral Basílica de Barcelona",
    "Jardí Botànic de Barcelona",
    "Parròquia de Santa Maria del Mar",
    "Museu Nacional d'Art de Catalunya",
    "Fundació Joan Miró",
    "Basílica de Santa Maria del Pi",
]

TARGET_MIN = 55
TARGET_MAX = 70


def _normalize(text: str) -> str:
    return text.lower().strip()


def _matches_any(name: str, keywords: list[str]) -> bool:
    normalized = _normalize(name)
    return any(kw in normalized for kw in keywords)


def _is_allowlisted(name: str) -> bool:
    normalized = _normalize(name)
    return any(_normalize(a) in normalized or normalized in _normalize(a) for a in ALLOWLIST_NAMES)


def filter_tourism_pois(df: pd.DataFrame) -> pd.DataFrame:
    """Return ~55-70 curated tourism POIs."""
    working = df.dropna(subset=["geo_epgs_4326_lat", "geo_epgs_4326_lon"]).copy()
    working = working[working["name"].notna()]

    allow_mask = working["name"].apply(_is_allowlisted)
    strong_mask = working["name"].apply(lambda n: _matches_any(n, STRONG_KEYWORDS))
    secondary_mask = working["name"].apply(lambda n: _matches_any(n, SECONDARY_KEYWORDS))
    outstanding_mask = working.get("values_outstanding", pd.Series(False, index=working.index)).astype(bool)
    exclude_mask = working["name"].apply(lambda n: _matches_any(n, EXCLUDE_KEYWORDS))

    include_mask = allow_mask | strong_mask | (outstanding_mask & secondary_mask)
    selected = working[include_mask & ~exclude_mask].copy()
    selected = selected.drop_duplicates(subset=["register_id"], keep="first")

    selected["_priority"] = (
        allow_mask.loc[selected.index].astype(int) * 100
        + outstanding_mask.loc[selected.index].astype(int) * 10
        + strong_mask.loc[selected.index].astype(int) * 5
        + secondary_mask.loc[selected.index].astype(int)
    )
    selected = selected.sort_values(["_priority", "name"], ascending=[False, True])

    if len(selected) > TARGET_MAX:
        selected = selected.head(TARGET_MAX)

    if len(selected) < TARGET_MIN:
        extra = working[secondary_mask & ~exclude_mask & ~working["register_id"].isin(selected["register_id"])]
        extra = extra.sort_values(["values_outstanding", "name"], ascending=[False, True])
        needed = TARGET_MIN - len(selected)
        selected = pd.concat([selected, extra.head(needed)], ignore_index=True)

    return selected.drop(columns=["_priority"], errors="ignore").reset_index(drop=True)
