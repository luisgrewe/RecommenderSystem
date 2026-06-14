"""Infer interest tags from POI names."""

from __future__ import annotations

import pandas as pd

TAG_RULES: list[tuple[str, list[str]]] = [
    ("religious", ["basílica", "basilica", "catedral", "cathedral", "església", "esglesia", "temple", "parròquia", "parroquia", "monestir", "sagrat cor", "sagrada família", "sagrada familia"]),
    ("museum", ["museu", "museum", "cosmocaixa", "memorial", "refugi"]),
    ("park", ["park", "parc", "jardí", "jardi", "botànic", "botanic"]),
    ("market", ["mercat", "market", "boqueria"]),
    ("architecture", ["casa ", "palau", "palace", "gaudí", "gaudi", "modernist", "modernista", "pedrera", "milà", "mila", "planells"]),
    ("beach", ["platja", "beach", "mar Bella", "barceloneta"]),
    ("history", ["born", "història", "historia", "refugi", "memorial", "model"]),
    ("viewpoint", ["mirador", "tibidabo", "bunkers", "telefèric", "teleferic", "funicular"]),
    ("nature", ["zoo", "aquàrium", "aquarium", "botànic", "botanic", "montjuïc", "montjuic"]),
    ("sport", ["camp nou", "estadi", "olímpic", "olimpic"]),
    ("entertainment", ["teatre", "theatre", "auditori", "fira", "exposició", "exposicio"]),
]


def infer_tags(name: str) -> set[str]:
    normalized = name.lower()
    tags: set[str] = set()
    for tag, keywords in TAG_RULES:
        if any(kw in normalized for kw in keywords):
            tags.add(tag)
    if not tags:
        tags.add("general")
    return tags


def add_interest_tags(df: pd.DataFrame, name_col: str = "name") -> pd.DataFrame:
    result = df.copy()
    result["interest_tags"] = result[name_col].map(lambda n: "|".join(sorted(infer_tags(str(n)))))
    return result
