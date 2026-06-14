# Report tables and figures — reproduction

How to regenerate quantitative results for the written report (especially **Table 3**: strategy comparison on the baseline scenario).

## Prerequisites

```bash
cd RecommenderSystem
source .venv/bin/activate
pip install -r requirements.txt
python scripts/build_data.py    # if data/processed/pois_simulation.csv is missing
```

## Run everything (recommended)

```bash
python scripts/run_all_reports.py
```

Runs batch simulation for all population scenarios (6 total), merges into `data/processed/batch_results.csv`, and writes `report/<scenario>/table3.csv` + `figure.png` for each.

Options:

| Flag | Effect |
|------|--------|
| `--reports-only` | Skip sims; rebuild `report/` from existing CSV |
| `--batch-only` | Run sims only; no tables/figures |
| `--scenarios baseline overtourism_peak` | Subset only |
| `--include-case-study` | Also run `seminar_religious` |

## Table 3 — main strategy comparison (baseline)

**What it shows:** Mean outcomes across random seeds for each recommender under the `baseline` scenario (3,000 agents, 5 days, 2 visits per agent per day).

**Metrics (columns):**

| Column | Meaning | Lower / higher is better? |
|--------|---------|----------------------------|
| `gini` | Inequality of visits across all 72 POIs | Lower = more even spread |
| `hotspot_pct` | Share of visits to five named landmarks (Sagrada Família, Casa Batlló, Park Güell, Boqueria, Museu Picasso) | Lower = less overtourism pressure on hotspots |
| `entropy` | Shannon entropy of visit distribution | Higher = more dispersed |
| `total_visits` | Sum of accepted visits over the run | Context only |
| `economic_impact` | Proxy spend (visits × ticket price) | Context only |
| `profile_consistency` | Share of top-k recommendations matching agent interest tags (sample tourist) | Higher = better profile fit |

**Seeds:** Defined in `config/simulation.yaml` under `batch.seeds` (default: 42, 7, 99, 123).

### Step 1 — run batch simulations

```bash
python scripts/run_batch.py --scenario baseline
```

This runs **3 strategies × 4 seeds = 12** full ABM simulations and appends rows to:

`data/processed/batch_results.csv`

Re-running the same scenario replaces only that scenario's rows; other scenarios are kept.

Each row contains: `scenario`, `strategy`, `seed`, and the metrics above.

Implementation: `scripts/run_batch.py` → `TourismModel.run()` → metrics in `src/metrics/`.

Console output also prints a mean-by-strategy summary when the run finishes.

### Step 2 — aggregate Table 3 (optional CSV)

```bash
python scripts/summarize_batch_results.py --scenario baseline
```

Writes `report/baseline/table3.csv` (mean ± std per strategy) and prints a markdown table to the terminal.

### Step 3 — figure for the report (recommended)

```bash
python scripts/plot_batch_results.py --scenario baseline
```

Writes:

- `report/baseline/figure.png` — insert into Word/LaTeX as **Figure 3**
- `report/baseline/figure.pdf` — vector version for LaTeX

Three panels: Gini, hotspot share (%), visit entropy. Error bars = std across seeds.

**Table vs figure:** Use the **table** for exact numbers (required for reproducibility). Add the **figure** if you have space — it makes the popularity vs sustainability trade-off obvious at a glance.

### Optional — stress scenario (Table 4)

```bash
python scripts/run_batch.py --scenario overtourism_peak
python scripts/summarize_batch_results.py --scenario overtourism_peak
python scripts/plot_batch_results.py --scenario overtourism_peak
```

Outputs go to `report/overtourism_peak/` (same filenames: `table3.csv`, `figure.png`).

## Case study table (top-3 POIs, one tourist)

No batch file — single recommender comparison for the `seminar_religious` profile:

```bash
python scripts/run_case_study.py --scenario seminar_religious
```

Use output for a qualitative **Table 5** (top-3 POI names per strategy). The dashboard **Your trip** panel shows the same comparison interactively.

## Figures (manual)

| Figure | Source |
|--------|--------|
| Architecture | Mermaid diagram in `README.md` |
| Bar chart (Gini / hotspot %) | `python scripts/plot_batch_results.py --scenario baseline` |
| Crowding maps | Solara screenshots: Popularity vs Sustainability after several **Next day** clicks |
| Demo video | Screen recording of `python -m solara run src/viz/app.py:Page --port 8765` |

## Changing experiment settings

| Setting | File |
|---------|------|
| Agents, days, travel budget | `config/scenarios.yaml` (per scenario) or `config/simulation.yaml` (defaults) |
| Strategies included | `config/simulation.yaml` → `recommenders.strategies` |
| Random seeds | `config/simulation.yaml` → `batch.seeds` |
| Sustainability MCDA weights | `config/simulation.yaml` → `sustainability_weights` |
| Hotspot POI names (for `hotspot_pct`) | `scripts/run_batch.py` → `HOTSPOT_SUBSTRINGS` |

After any config change, re-run Step 1 and Step 2 so report numbers match the codebase.

## File reference

| Path | Role |
|------|------|
| `data/processed/batch_results.csv` | Raw batch output (one row per strategy × seed) |
| `report/baseline/table3.csv` | Table 3 (mean ± std by strategy) |
| `report/baseline/figure.png` | Figure: Gini, hotspot %, entropy bars |
| `scripts/run_batch.py` | Generates raw batch results |
| `scripts/summarize_batch_results.py` | Aggregates CSV + markdown table |
| `scripts/run_all_reports.py` | All scenarios: batch + report outputs |
