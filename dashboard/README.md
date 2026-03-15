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

Use the SQL in `/sql/export_queries.sql` to create the extracts.
