# ML Forecasting Sprint 4

## Objective

Expose `baseline_ml_dynamic_risk` in the Streamlit dashboard while preserving
existing scoring and training logic.

## Scope Implemented

- Added scenario selection support in forecast-facing dashboard views:
  - `baseline_static_risk` (default)
  - `baseline_ml_dynamic_risk` (when present in exported files)
- Added clear scenario labels in the UI:
  - "Static baseline: governance, climate, adaptation, and conflict are carried forward where no external projection exists."
  - "ML dynamic risk: climate vulnerability uses validated ML projection where available; governance, adaptation, and conflict remain carried forward."
- Added graceful scenario filtering logic that combines:
  - historical rows (`historical_observed`)
  - selected forecast scenario rows
- Added optional comparison section in Global Overview using:
  - `gold__scenario_delta_country_2045`
  - `gold__scenario_delta_summary`
- Added robust fallback handling if comparison exports are missing.

## Dashboard Data Contract Updates

Optional new export files:

- `scenario_delta_summary.parquet` or `.csv`
- `scenario_delta_country_2045.parquet` or `.csv`

Country score export now supports projection metadata columns when available:

- `climate_vulnerability_projection_source`
- `climate_vulnerability_forecast_method`

## Explicit Non-Changes

- No changes to ML training code.
- No changes to dbt scoring SQL.
- No changes to seed artifacts or scenario logic.
