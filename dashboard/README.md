---
title: World2045 Dashboard
emoji: 🌍
colorFrom: indigo
colorTo: blue
sdk: docker
app_port: 7860
pinned: false
---

# World2045 Dashboard

A lightweight Streamlit dashboard for the World2045 academic project.

## Run locally

```bash
pip install -r requirements.txt
streamlit run app/app.py
```

## Data contract

Place small precomputed files in `/data` (CSV or parquet):

- `global_year.parquet`
- `region_year.parquet`
- `country_scores.parquet`
- `country_components.parquet`
- `quadrants.parquet`
- `rankings.parquet`
- `doomsday_clock.csv`
- `scenario_delta_summary.parquet` (optional, for Sprint 4 comparison view)
- `scenario_delta_country_2045.parquet` (optional, for Sprint 4 comparison view)

Forecast scenario behavior in dashboard:

- Default: `baseline_static_risk`
- Optional selectable: `baseline_ml_dynamic_risk` when present in extracts
- Historical rows (`historical_observed`) are retained and shown together with the selected forecast scenario.

Use the SQL in `/sql/export_queries.sql` to create the extracts.
