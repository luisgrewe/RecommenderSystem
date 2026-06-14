"""In-app help text for scenarios, strategies, and metrics."""

STRATEGY_HELP: dict[str, dict[str, str]] = {
    "popularity": {
        "title": "Popularity-based",
        "summary": "Ranks POIs by global fame (TripAdvisor-style hotspots). Ignores personal interests unless filtered by budget.",
        "behavior": "Sends most tourists to Sagrada Família, Park Güell, Boqueria, etc. Expect high hotspot share and Gini.",
        "try_with": "baseline or overtourism_peak — use as the baseline to beat.",
    },
    "interest_based": {
        "title": "Interest-based",
        "summary": "Matches POIs to each tourist's interest tags (religious, museum, park…). Penalises crowded or distant places.",
        "behavior": "Personalised lists, but still ignores city-wide sustainability. Good profile fit, moderate spreading.",
        "try_with": "seminar_religious or crowd_averse — shows personalised religious/cultural routes.",
    },
    "sustainability": {
        "title": "Sustainability-aware",
        "summary": "Multi-criteria scorer: interests + environment + local culture/economy + live crowding dispersion.",
        "behavior": "Steers tourists away from overtourism hotspots toward lesser-known but relevant POIs. Low hotspot share.",
        "try_with": "baseline vs popularity — compare metrics after several Run day clicks.",
    },
}

METRICS_HELP: dict[str, str] = {
    "Total visits": "All POI visits counted across every agent since the run started.",
    "Hotspot share": "% of visits to famous crowded sites (Sagrada, Casa Batlló, Park Güell, Boqueria, Picasso). Lower is better for overtourism.",
    "Crowding Gini": "How unequal visits are across POIs (0 = even spread, 1 = very concentrated). Lower means better city-wide distribution.",
    "Simulation day": "Current day of the simulated trip. Click Run day to advance and watch metrics update.",
}

SCENARIO_HELP_EXTRA: dict[str, str] = {
    "baseline": (
        "Default city-wide test: thousands of tourists with mixed interests and moderate "
        "crowd sensitivity. Use this to compare all three recommender strategies fairly."
    ),
    "seminar_religious": (
        "Seminar example — set interests to Religious, Architecture, History in "
        "'Your trip' and compare strategies for that profile."
    ),
    "crowd_averse": (
        "Most tourists strongly dislike crowds. They skip busy POIs even when recommended. "
        "Shows how crowd sensitivity interacts with the recommender."
    ),
    "budget_backpacker": (
        "Low budget (€8 max ticket). Expensive POIs like Casa Batlló are filtered out. "
        "Popularity may still suggest famous names but agents cannot afford them."
    ),
    "family_with_kids": (
        "Families prefer parks and outdoor activities, travel shorter distances. "
        "Good for testing whether recommenders suggest Ciutadella, beaches, etc."
    ),
    "overtourism_peak": (
        "Stress test: 8000 tourists, 7 days, city already under pressure. "
        "Combine with Popularity to see red hotspots; then switch to Sustainability to compare relief."
    ),
    "sustainability_mission": (
        "Eco-conscious tourists who strongly weight sustainability in scores. "
        "Amplifies the effect of the sustainability-aware recommender."
    ),
}


def strategy_help_for(strategy_id: str) -> dict[str, str]:
    return STRATEGY_HELP.get(strategy_id, {"title": strategy_id, "summary": "", "behavior": "", "try_with": ""})
