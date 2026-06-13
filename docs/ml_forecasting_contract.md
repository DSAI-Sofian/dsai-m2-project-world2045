# ML Forecasting Contract (Sprint 1)

## Purpose

This document defines the Sprint 1 structural-risk forecasting contract for the World2045 ML upgrade.
It introduces a placeholder table schema for future ML projections while preserving the current baseline scoring behavior.

## Baseline Parity Guarantee

The existing scenario scoring model remains unchanged:

- `dbt/models/gold/analysis/gold__country_trajectory_score_year_scenario.sql`

Current baseline carry-forward logic remains in place for forecast years (2024-2045):

- latest-observed state extraction: `latest_observed_state` CTE
- carry-forward join for forecast rows: `forecast_base` CTE
- carried components:
  - `vdem_liberal_democracy_index`
  - `adaptation_readiness`
  - `climate_vulnerability`
  - `conflict_severity`

No dashboard, ranking, or scenario output behavior is changed in Sprint 1.

## New Placeholder Contract Model

Model:

- `dbt/models/silver/projections/silver__projection_structural_risk_country_year.sql`

Grain:

- one row per (`country_iso3`, `year`, `scenario_id`, `indicator_name`)

Forecast window:

- years `2024` to `2045`

Indicators covered in Sprint 1 contract:

- `vdem_liberal_democracy_index`
- `adaptation_readiness`
- `climate_vulnerability`
- `conflict_severity`

Contract fields:

- `country_iso3`
- `year`
- `scenario_id`
- `indicator_name`
- `projected_value`
- `projection_source`
- `forecast_method`
- `model_version`
- `created_at`

Sprint 1 placeholder values:

- `scenario_id = 'baseline_static_risk'`
- `projected_value = null`
- `projection_source = 'world2045_sprint1_contract_placeholder'`
- `forecast_method = 'ml_placeholder'`
- `model_version = 'sprint1_contract_v1'`

## Schema Tests (Sprint 1)

Defined in:

- `dbt/models/silver/projections/_projection_models.yml`

Tests added:

- not null keys and metadata fields
- uniqueness at contract grain
- year range validation (`2024` to `2045`)
- accepted values for:
  - `scenario_id`
  - `indicator_name`
  - `forecast_method`

## Out of Scope for Sprint 1

- ML training or inference code
- scenario model integration with ML projections
- dashboard changes
