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

## Export refresh tip

If you export with `bq query`, set a high `--max_rows` value (for example
`--max_rows=500000`) so files are not truncated to the default preview limit.

## Example export refresh flow

From repository root:

```bash
bq query --nouse_legacy_sql --format=csv --max_rows=500000 \
  "SELECT year, avg_trajectory_score AS trajectory_score, country_count, scenario_id, is_forecast_year
   FROM \`world2045_ci.gold__trajectory_global_year\`
   ORDER BY year, scenario_id" > dashboard/data/global_year.csv
```

Repeat for the other export queries in `dashboard/sql/export_queries.sql`.

## Scenario switching in app

- Open `Global Overview`, `Country Explorer`, or `Regional View`.
- Use the `Forecast scenario` selector.
- Default is `baseline_static_risk`.
- Select `baseline_ml_dynamic_risk` to compare climate-ML-enhanced forecasts.

## How to interpret scenario deltas

- In `Global Overview`, review `Scenario Comparison (2045)`.
- `avg_score_delta` and country-level score/rank deltas are computed as:
  - ML dynamic risk minus static baseline.
- Treat this as comparative sensitivity analysis, not definitive forecast truth.
