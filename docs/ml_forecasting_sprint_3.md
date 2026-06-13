# ML Forecasting Sprint 3

## Objective

Integrate only the validated `climate_vulnerability` ML forecast into the
gold scenario scoring layer while preserving the existing
`baseline_static_risk` behavior unchanged.

## Scenario Design

Model updated:

- `dbt/models/gold/analysis/gold__country_trajectory_score_year_scenario.sql`

Scenarios:

- `historical_observed` (unchanged)
- `baseline_static_risk` (unchanged carry-forward baseline)
- `baseline_ml_dynamic_risk` (new)

## Integration Rule

For `baseline_ml_dynamic_risk` in forecast years (`2024-2045`):

- `climate_vulnerability = coalesce(ml_projection, carry_forward_climate_vulnerability)`
- `vdem_liberal_democracy_index` stays carry-forward
- `adaptation_readiness` stays carry-forward
- `conflict_severity` stays carry-forward

ML projection source:

- `silver__projection_structural_risk_country_year`
- filtered to `scenario_id = baseline_ml_dynamic_risk`
- filtered to `indicator_name = climate_vulnerability`

## Projection Metadata

Added output fields:

- `climate_vulnerability_projection_source`
- `climate_vulnerability_forecast_method`

## Baseline Parity Protection

To prevent ML scenario rows from altering static normalization bounds, the
normalization stats are computed by:

- `scenario_id`
- `year`

This keeps `baseline_static_risk` bounds isolated from `baseline_ml_dynamic_risk`.

## New dbt Tests

Singular tests added:

- `dbt/tests/test_gold__country_trajectory_score_year_scenario__forecast_scenario_ids.sql`
  - validates forecast scenario ids
- `dbt/tests/test_gold__country_trajectory_score_year_scenario__forecast_coverage_parity.sql`
  - validates same country-year coverage between static and ML scenarios

## Comparison Outputs

Added models:

- `gold__scenario_delta_country_2045`
  - country-level score/rank deltas between static and ML scenarios
- `gold__scenario_delta_summary`
  - global and region-level delta summary

## Inputs Added

Seed added for validated Sprint 2B climate projections:

- `dbt/seeds/ml_climate_vulnerability_projection_2024_2045.csv`

This seed is consumed by `silver__projection_structural_risk_country_year`.

## Explicit Non-Changes

- no dashboard file changes
- no integration of adaptation/governance/conflict ML projections
