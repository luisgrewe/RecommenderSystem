"""Shared dashboard styles and labels."""

GLOBAL_CSS = """
:root {
  --bg-page: #0f1419;
  --bg-panel: #1a2332;
  --bg-card: #243044;
  --border: #334155;
  --text: #e2e8f0;
  --text-muted: #94a3b8;
  --accent: #38bdf8;
  --accent-2: #34d399;
  --warn: #fbbf24;
  --danger: #f87171;
  --radius: 12px;
  --font: "Inter", "Segoe UI", system-ui, sans-serif;
}

.dashboard-root {
  font-family: var(--font);
  background: var(--bg-page);
  color: var(--text);
  min-height: 100vh;
  padding: 0;
  margin: 0;
}

.dashboard-header {
  background: linear-gradient(135deg, #1e3a5f 0%, #0f172a 100%);
  border-bottom: 1px solid var(--border);
  padding: 0.85rem 1.75rem;
}

.dashboard-header h1 {
  margin: 0;
  font-size: 1.25rem;
  font-weight: 700;
  letter-spacing: -0.02em;
  color: #ffffff;
}

.dashboard-header p {
  margin: 0.35rem 0 0;
  color: #cbd5e1;
  font-size: 0.9rem;
}

.dashboard-body {
  display: flex;
  flex-wrap: wrap;
  gap: 1rem;
  padding: 1.25rem 1.75rem 2rem;
  align-items: flex-start;
}

.sidebar {
  flex: 0 0 340px;
  max-width: 100%;
  background: var(--bg-panel);
  border: 1px solid var(--border);
  border-radius: var(--radius);
  padding: 1.25rem;
}

.sidebar h2 {
  margin: 0 0 0.65rem;
  font-size: 0.75rem;
  text-transform: uppercase;
  letter-spacing: 0.08em;
  color: var(--text-muted);
  font-weight: 600;
}

.sidebar-run {
  padding-bottom: 0.85rem;
  margin-bottom: 0.85rem;
  border-bottom: 1px solid var(--border);
}

.sidebar-run h2 {
  margin-bottom: 0.5rem;
}

.sidebar section {
  margin-bottom: 1rem;
}

.hint-line {
  font-size: 0.72rem;
  color: #64748b;
  line-height: 1.35;
  margin: 0.15rem 0 0.65rem;
  overflow: hidden;
  text-overflow: ellipsis;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
}

.metrics-hint {
  font-size: 0.72rem;
  color: #64748b;
  margin: -0.35rem 0 0.85rem;
  line-height: 1.45;
  padding: 0.5rem 0.65rem;
  background: #1e293b;
  border-radius: 8px;
  border-left: 3px solid #475569;
}

.metrics-hint strong {
  color: #94a3b8;
  font-weight: 600;
}

.btn-row-primary {
  margin-top: 0.35rem;
}

.main-panel {
  flex: 1 1 520px;
  min-width: 0;
}

.metrics-row {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(140px, 1fr));
  gap: 0.75rem;
  margin-bottom: 1rem;
}

.metric-card {
  background: var(--bg-card);
  border: 1px solid var(--border);
  border-radius: var(--radius);
  padding: 0.85rem 1rem;
}

.metric-card .label {
  font-size: 0.7rem;
  text-transform: uppercase;
  letter-spacing: 0.06em;
  color: var(--text-muted);
  margin-bottom: 0.25rem;
}

.metric-card .value {
  font-size: 1.35rem;
  font-weight: 700;
  color: var(--accent);
}

.metric-card .value.green { color: var(--accent-2); }
.metric-card .value.warn { color: var(--warn); }
.metric-card .value.danger { color: var(--danger); }

.metric-card .metric-hint {
  font-size: 0.65rem;
  color: #64748b;
  line-height: 1.3;
  margin-top: 0.35rem;
}

.map-wrap {
  background: var(--bg-panel);
  border: 1px solid var(--border);
  border-radius: var(--radius);
  overflow: hidden;
  padding: 0.5rem;
}

.scenario-desc {
  font-size: 0.85rem;
  color: #cbd5e1;
  line-height: 1.45;
  margin-top: 0.5rem;
  padding: 0.75rem;
  background: var(--bg-card);
  border-radius: 8px;
  border-left: 3px solid var(--accent);
}

.help-box {
  font-size: 0.8rem;
  color: #cbd5e1;
  line-height: 1.45;
  margin-top: 0.65rem;
  padding: 0.7rem 0.75rem;
  background: var(--bg-card);
  border-radius: 8px;
  border-left: 3px solid var(--accent);
}

.help-box.strategy {
  border-left-color: var(--accent-2);
}

.help-box.connection {
  border-left-color: var(--accent);
  margin-bottom: 0.85rem;
  font-size: 0.75rem;
}

.help-box.connection p {
  margin: 0.35rem 0 0;
}

.help-box.connection p:first-of-type {
  margin-top: 0.5rem;
}

.help-box.connection em {
  color: #cbd5e1;
  font-style: normal;
  font-weight: 600;
}

.field-active {
  font-size: 0.68rem;
  color: #6ee7b7;
  margin: -0.35rem 0 0.55rem;
  line-height: 1.35;
}

.field-muted {
  font-size: 0.68rem;
  color: #64748b;
  margin: -0.35rem 0 0.55rem;
  line-height: 1.35;
}

.rec-panel-note {
  font-size: 0.75rem;
  color: #94a3b8;
  line-height: 1.45;
  margin: -0.35rem 0 0.75rem;
  padding: 0.5rem 0.65rem;
  background: #1e293b;
  border-radius: 8px;
  border-left: 3px solid var(--accent);
}

.rec-panel-note strong {
  color: #e2e8f0;
}

.help-box.metrics {
  border-left-color: var(--text-muted);
  margin-top: 0;
}

.help-box strong {
  display: block;
  color: #ffffff;
  font-size: 0.82rem;
  margin-bottom: 0.35rem;
}

.help-box p {
  margin: 0 0 0.45rem;
}

.help-box p:last-child {
  margin-bottom: 0;
}

.help-box em {
  color: #94a3b8;
  font-style: normal;
  font-weight: 600;
  font-size: 0.72rem;
  text-transform: uppercase;
  letter-spacing: 0.04em;
}

.scenario-desc strong {
  color: #ffffff;
}

.legend {
  display: flex;
  flex-wrap: wrap;
  gap: 1rem;
  font-size: 0.8rem;
  color: var(--text-muted);
}

.map-legend {
  margin-top: 0.35rem;
  margin-bottom: 0.75rem;
  padding: 0.35rem 0.5rem;
}

.legend-item {
  display: flex;
  align-items: center;
  gap: 0.4rem;
}

.legend-dot {
  width: 10px;
  height: 10px;
  border-radius: 50%;
}

.btn-row {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
  margin-top: 0.5rem;
}

.empty-state {
  text-align: center;
  padding: 3rem 1rem;
  color: #e2e8f0;
  background: var(--bg-panel);
  border: 1px dashed var(--border);
  border-radius: var(--radius);
}

.footer-note {
  margin-top: 0.75rem;
  font-size: 0.85rem;
  color: #cbd5e1;
}

.footer-note strong {
  color: #ffffff;
}

/* --- Solara / Vuetify controls on dark panels --- */
.dashboard-root {
  color: #f1f5f9;
}

.sidebar .v-label,
.sidebar .v-field-label,
.sidebar .v-label--active,
.sidebar label {
  color: #f8fafc !important;
  opacity: 1 !important;
}

.sidebar .v-field__input,
.sidebar .v-select__selection-text,
.sidebar .v-select__selection,
.sidebar .v-slider__thumb-label div {
  color: #f1f5f9 !important;
}

.sidebar .v-field--variant-filled .v-field__overlay,
.sidebar .v-field {
  background: #243044 !important;
}

.sidebar .v-field__outline {
  color: #64748b !important;
}

.sidebar .v-slider-track__fill {
  background: var(--accent) !important;
}

.sidebar .v-slider-thumb__surface {
  background: var(--accent) !important;
}

.dashboard-root .solara-markdown,
.dashboard-root .solara-markdown p,
.dashboard-root .solara-markdown em,
.dashboard-root .solara-markdown strong {
  color: #e2e8f0 !important;
}

.dashboard-root .solara-markdown strong {
  color: #ffffff !important;
}

.main-panel .empty-state .solara-markdown p {
  color: #e2e8f0 !important;
}

.insights-row {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1rem;
  margin-top: 1rem;
}

@media (max-width: 960px) {
  .insights-row { grid-template-columns: 1fr; }
}

.insights-panel {
  background: var(--bg-panel);
  border: 1px solid var(--border);
  border-radius: var(--radius);
  padding: 1rem 1.15rem;
}

.insights-panel h3 {
  margin: 0 0 0.75rem;
  font-size: 0.8rem;
  text-transform: uppercase;
  letter-spacing: 0.07em;
  color: #94a3b8;
  font-weight: 600;
}

.insight-banner {
  background: #1e3a5f;
  border: 1px solid #334155;
  border-left: 4px solid var(--accent);
  border-radius: 8px;
  padding: 0.75rem 1rem;
  margin-bottom: 1rem;
  font-size: 0.85rem;
  color: #e2e8f0;
  line-height: 1.5;
}

.rec-item {
  background: var(--bg-card);
  border-radius: 8px;
  padding: 0.65rem 0.75rem;
  margin-bottom: 0.5rem;
  border-left: 3px solid var(--accent);
}

.rec-item.caution { border-left-color: var(--warn); }
.rec-item.likely_skip { border-left-color: var(--danger); opacity: 0.9; }
.rec-item.must_visit { border-left-color: #a78bfa; }
.rec-item.blocked { border-left-color: var(--danger); opacity: 0.85; }

.rec-item .rec-title {
  font-weight: 600;
  color: #f8fafc;
  font-size: 0.88rem;
  margin-bottom: 0.25rem;
}

.rec-item .rec-meta {
  font-size: 0.75rem;
  color: #94a3b8;
  margin-bottom: 0.35rem;
}

.rec-item .rec-reasons {
  font-size: 0.75rem;
  color: #cbd5e1;
  line-height: 1.4;
}

.badge {
  display: inline-block;
  font-size: 0.65rem;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  padding: 0.15rem 0.45rem;
  border-radius: 4px;
  margin-right: 0.35rem;
  font-weight: 600;
}

.badge.recommended { background: #065f46; color: #6ee7b7; }
.badge.caution { background: #78350f; color: #fcd34d; }
.badge.likely_skip { background: #7f1d1d; color: #fca5a5; }
.badge.must_visit { background: #4c1d95; color: #ddd6fe; }
.badge.blocked { background: #7f1d1d; color: #fca5a5; }

.crowded-row {
  display: flex;
  justify-content: space-between;
  font-size: 0.8rem;
  padding: 0.35rem 0;
  border-bottom: 1px solid #334155;
  color: #e2e8f0;
}

.crowded-row span.muted { color: #94a3b8; }

/* --- City snapshot --- */
.snapshot-section {
  margin-bottom: 1.1rem;
}

.snapshot-section.strategy-section {
  margin-bottom: 0;
  padding-top: 0.25rem;
}

.snapshot-section-head {
  display: flex;
  align-items: flex-start;
  gap: 0.55rem;
  margin-bottom: 0.75rem;
}

.snapshot-icon {
  font-size: 1.05rem;
  line-height: 1.2;
  opacity: 0.9;
}

.snapshot-section-title {
  font-size: 0.82rem;
  font-weight: 600;
  color: #f1f5f9;
  letter-spacing: 0.01em;
}

.snapshot-section-sub {
  font-size: 0.72rem;
  color: #64748b;
  margin-top: 0.15rem;
  line-height: 1.35;
}

.snapshot-placeholder {
  text-align: center;
  padding: 1.25rem 1rem;
  margin-bottom: 1rem;
  background: var(--bg-card);
  border: 1px dashed #475569;
  border-radius: 10px;
  color: #94a3b8;
  font-size: 0.8rem;
  line-height: 1.45;
}

.snapshot-placeholder-icon {
  font-size: 1.5rem;
  margin-bottom: 0.35rem;
}

.snapshot-placeholder strong {
  display: block;
  color: #e2e8f0;
  font-size: 0.85rem;
  margin-bottom: 0.35rem;
}

.snapshot-placeholder p {
  margin: 0;
}

.snapshot-empty {
  font-size: 0.78rem;
  color: #94a3b8;
  padding: 0.65rem 0.75rem;
  background: var(--bg-card);
  border-radius: 8px;
}

.crowded-list {
  display: flex;
  flex-direction: column;
  gap: 0.45rem;
}

.crowded-card {
  display: flex;
  align-items: flex-start;
  gap: 0.55rem;
  background: var(--bg-card);
  border: 1px solid #334155;
  border-radius: 10px;
  padding: 0.55rem 0.65rem;
  transition: border-color 0.15s ease;
}

.crowded-card:hover {
  border-color: #475569;
}

.crowded-rank {
  flex: 0 0 1.35rem;
  height: 1.35rem;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 0.68rem;
  font-weight: 700;
  color: #94a3b8;
  background: #1e293b;
  border-radius: 6px;
}

.crowded-body {
  flex: 1;
  min-width: 0;
}

.crowded-name {
  font-size: 0.8rem;
  font-weight: 600;
  color: #f8fafc;
  margin-bottom: 0.35rem;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.crowd-bar-track {
  height: 5px;
  background: #1e293b;
  border-radius: 999px;
  overflow: hidden;
  margin-bottom: 0.4rem;
}

.crowd-bar-fill {
  height: 100%;
  border-radius: 999px;
  transition: width 0.3s ease;
}

.crowd-bar-fill.low { background: var(--accent-2); }
.crowd-bar-fill.moderate { background: var(--warn); }
.crowd-bar-fill.high { background: var(--danger); }

.crowded-stats {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 0.35rem 0.5rem;
  font-size: 0.7rem;
  color: #94a3b8;
}

.crowd-pill {
  display: inline-block;
  font-size: 0.65rem;
  font-weight: 600;
  padding: 0.12rem 0.4rem;
  border-radius: 999px;
  letter-spacing: 0.02em;
}

.crowd-pill.low { background: #064e3b; color: #6ee7b7; }
.crowd-pill.moderate { background: #78350f; color: #fcd34d; }
.crowd-pill.high { background: #7f1d1d; color: #fca5a5; }

.district-chip {
  margin-left: auto;
  font-size: 0.65rem;
  padding: 0.1rem 0.4rem;
  background: #1e293b;
  border-radius: 4px;
  color: #cbd5e1;
}

.strategy-compare {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 0.55rem;
}

@media (max-width: 520px) {
  .strategy-compare { grid-template-columns: 1fr; }
}

.strategy-col {
  background: var(--bg-card);
  border: 1px solid #334155;
  border-radius: 10px;
  padding: 0.65rem 0.75rem;
  border-top: 3px solid #475569;
}

.strategy-col.popularity {
  border-top-color: var(--warn);
}

.strategy-col.current {
  border-top-color: var(--accent-2);
}

.strategy-col-title {
  font-size: 0.72rem;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  color: #94a3b8;
  margin-bottom: 0.5rem;
}

.strategy-col ul {
  list-style: none;
  margin: 0;
  padding: 0;
}

.strategy-col li {
  display: flex;
  align-items: baseline;
  gap: 0.4rem;
  font-size: 0.78rem;
  color: #e2e8f0;
  line-height: 1.4;
  padding: 0.3rem 0;
  border-bottom: 1px solid #2d3748;
}

.strategy-col li:last-child {
  border-bottom: none;
  padding-bottom: 0;
}

.strategy-poi-rank {
  flex: 0 0 auto;
  font-size: 0.65rem;
  font-weight: 700;
  color: #64748b;
}

.strategy-poi-empty {
  font-size: 0.75rem;
  color: #64748b;
  font-style: italic;
}

.compare-block {
  margin-top: 0.75rem;
  padding-top: 0.75rem;
  border-top: 1px solid #334155;
  font-size: 0.8rem;
  color: #cbd5e1;
}

.compare-block strong { color: #f8fafc; }
"""

STRATEGY_LABELS = {
    "popularity": "Popularity-based",
    "interest_based": "Interest-based",
    "sustainability": "Sustainability-aware",
}

HOTSPOT_SUBSTRINGS = [
    "Sagrada Família",
    "Casa Batlló",
    "Park Güell",
    "Boqueria",
    "Museu Picasso",
]
