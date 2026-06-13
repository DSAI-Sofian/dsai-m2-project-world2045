# ML Forecasting Sprint 2 / 2B

## Objective

Sprint 2 introduces the first real ML forecasting workflow for structural-risk indicators while keeping the current gold scenario scoring layer unchanged.
Sprint 2B hardens the workflow with random-forest evaluation, rolling-origin validation, regional diagnostics, and forecast sanity checks.

## Scope Delivered

- Built ML-ready country-year panel for:
  - `vdem_liberal_democracy_index`
  - `adaptation_readiness`
  - `climate_vulnerability`
- Added lag, rolling means, multi-year changes, and missingness flags.
- Added training/backtesting script:
  - `scripts/train_structural_ml_forecasts.py`
- Produced forecast contract artifact for `2024-2045` using:
  - `scenario_id = baseline_ml_dynamic_risk`
- Produced validation outputs:
  - rolling-origin metrics with explicit train/test folds
  - model selection decision report (`integrate`, `keep carry-forward`, `defer`)
  - regional MAE diagnostics and ML-worse-than-baseline report
  - forecast sanity and coverage reports

## Data Inputs

Local sources used by training script:

- `data/raw/vdem/vdem_country_year.csv`
- `data/bronze/nd_gain_country_year.parquet`

dbt ML panel model:

- `dbt/models/silver/projections/silver__ml_structural_risk_panel_country_year.sql`

This model references:

- `silver__fact_governance_country_year`
- `silver__fact_climate_risk_country_year`
- `fact_country_year_spine`

## Feature Engineering

For each (`country_iso3`, `indicator_name`, `year`):

- `prev_year_value`
- `rolling_mean_3y`
- `rolling_mean_5y`
- `change_3y`
- `change_5y`
- `is_prev_year_missing`
- `is_rolling_mean_3y_missing`
- `is_rolling_mean_5y_missing`
- target missingness flag: `is_indicator_missing`

## Modeling Strategy

Baseline model:

- carry-forward (`value[t] = value[t-1]`)

ML models:

- linear regression
- ridge regression
- random forest if scikit-learn is available

Implementation note:

- script runs without scikit-learn by using numpy linear/ridge implementations
- if scikit-learn is installed, sklearn models are included automatically

## Rolling-Origin Validation

Folds used in Sprint 2B:

- train to 2005, test 2006-2010
- train to 2010, test 2011-2015
- train to 2015, test 2016-2020
- train to 2020, test 2021-2023

## Selection Rule

Per indicator:

- evaluate models on rolling-origin folds
- compare against carry-forward baseline at indicator and fold level
- decision outcomes:
  - `integrate`: meaningful and stable improvement vs carry-forward
  - `keep carry-forward`: ML underperforms baseline
  - `defer`: ML improvement exists but is too small or unstable

## Outputs

Generated under `data/processed/ml/`:

- `structural_risk_ml_panel_country_year.csv`
- `rolling_origin_prediction_rows.csv`
- `rolling_origin_metrics.csv`
- `rolling_origin_metrics_summary.csv`
- `regional_metrics.csv`
- `regional_ml_worse_than_carry_forward.csv`
- `model_selection_decision.csv`
- `coverage_report_by_indicator.csv`
- `forecast_sanity_thresholds.csv`
- `forecast_sanity_report.csv`
- `structural_risk_forecast_contract_2024_2045.csv`
- `run_summary.json`

Contract fields in forecast artifact:

- `country_iso3`
- `year`
- `scenario_id`
- `indicator_name`
- `projected_value`
- `projection_source`
- `forecast_method`
- `model_version`
- `created_at`

## Explicit Non-Changes

- no change to `gold__country_trajectory_score_year_scenario.sql`
- no dashboard file changes
- no gold scoring integration in Sprint 2
