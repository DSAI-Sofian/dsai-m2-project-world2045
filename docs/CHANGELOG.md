# CHANGELOG

## Phase 0 - Repository and Platform Setup

- initialized GitHub repository and branch structure
- configured dbt project scaffolding
- configured BigQuery target environment
- implemented GitHub Actions dbt CI workflow
- stabilized CI and dbt project layout
- documented environment setup, repo hygiene, and execution conventions

## Phase 1 - Population and Economic Backbone

- integrated core population ingestion and transformation
- integrated WDI-based economic indicators
- standardized country-year conformance across backbone models
- created core silver and gold tables to support the first analytical mart
- validated row coverage and year coverage for historical backbone tables

## Phase 2 - Governance, Inequality, and HDI Extension

- integrated governance indicators from V-Dem
- integrated inequality indicators from WID
- integrated HDI series and alignment fields
- built broader analytical feature coverage in the gold mart
- improved documentation around indicator mapping and model patterns

## Phase 3 - Climate and Conflict Integration

- integrated ND-GAIN climate measures
- integrated UCDP conflict measures
- extended country-year analytical feature mart with:
  - climate vulnerability
  - adaptation readiness
  - battle deaths
  - conflict incidence
- validated climate/conflict year coverage and population of the feature mart

## Phase 4 - Forecast Feature Extension

- integrated projection datasets for 2024-2045
- built `silver__projection_population_country_year`
- built `silver__projection_gdp_country_year_annualized`
- built `gold__forecast_feature_country_year`
- derived projected GDP per capita using projected GDP and projected population
- validated forecast coverage years and row counts

## Phase 5 - Historical Trajectory Model

- implemented `gold__country_trajectory_score_year`
- limited historical scoring window to 1995-2023 because climate indicators begin in 1995
- adopted per-year min-max normalization
- transformed conflict using `ln(1 + battle_deaths)`
- implemented weighted composite trajectory score
- ran analytical queries for:
  - top improvers since 1995
  - climate penalties
  - governance contributions

## Phase 6 - Scenario-Based Forward Trajectory Model

- implemented `gold__country_trajectory_score_year_scenario`
- preserved historical observed period and added 2024-2045 forecast period
- used direct forecast values for GDP per capita and life expectancy
- used carried-forward baseline values for governance, adaptation readiness, climate vulnerability, and conflict severity
- added `scenario_id`, `is_forecast_year`, `assumption_flag`, and `forecast_score_completeness`
- validated scenario coverage and completeness

## Phase 7 - Regional and Subregional Aggregation

- implemented `gold__region_trajectory_score_year`
- implemented subregional regionalization logic
- diagnosed and fixed inherited clustering issue in dbt model config
- filtered regional analysis to mapped sovereign entities for cleaner interpretation
- validated region and subregion outputs for 1995, 2023, and 2045 checkpoints

## Phase 8 - Strategic Ranking Layer

- implemented `gold__country_rise_potential`
- implemented `gold__country_trajectory_momentum`
- validated top 25 country rankings and top 10 by region
- identified Guyana as the standout high-momentum outlier
- documented distinction between strategic position and momentum

## Phase 9 - Quadrant Segmentation and Dashboard-Ready Models

- implemented `gold__trajectory_country_quadrant`
- revised thresholding from means to medians for cleaner segmentation
- produced final quadrant distribution and regional quadrant mix
- built dashboard-ready support marts:
  - `gold__trajectory_global_year`
  - `gold__trajectory_component_breakdown`

## Phase 10 - Documentation and Training Layer

- prepared user README
- prepared technical README
- prepared training manual with validation SQL
- prepared final analytical findings with validation SQL aligned to each conclusion

## Phase 11 - ML Upgrade Sprint 1 (Contract and Baseline Parity)

- added placeholder structural-risk projection contract model:
  - `silver__projection_structural_risk_country_year`
- defined contract fields for future ML forecast integration:
  - `country_iso3`, `year`, `scenario_id`, `indicator_name`, `projected_value`
  - `projection_source`, `forecast_method`, `model_version`, `created_at`
- added schema tests for contract integrity:
  - not null keys and metadata fields
  - unique contract grain
  - forecast year range (2024-2045)
  - accepted values for scenario, indicator, and forecast method
- preserved existing baseline scenario behavior:
  - no change to `gold__country_trajectory_score_year_scenario`
  - carry-forward assumptions remain authoritative for `baseline_static_risk`
- added Sprint 1 contract documentation:
  - `docs/ml_forecasting_contract.md`

## Phase 12 - ML Upgrade Sprint 2 (Governance and Climate Forecasting)

- added ML-ready panel model for structural-risk indicators:
  - `silver__ml_structural_risk_panel_country_year`
- engineered panel features:
  - previous-year value
  - 3-year and 5-year rolling means
  - 3-year and 5-year changes
  - missingness flags
- added Sprint 2 training and forecasting script:
  - `scripts/train_structural_ml_forecasts.py`
- implemented model benchmark workflow:
  - carry-forward baseline
  - linear and ridge regression (numpy fallback)
  - random forest when scikit-learn is available
- generated Sprint 1 contract-shaped forecast artifact for:
  - years 2024-2045
  - scenario `baseline_ml_dynamic_risk`
- generated Sprint 2 validation artifacts:
  - backtest metrics for 2010-2023
  - indicator-level ML vs carry-forward comparison
  - forecast coverage by indicator
- added Sprint 2 documentation:
  - `docs/ml_forecasting_sprint_2.md`
- preserved baseline behavior:
  - no integration into gold scenario scoring model yet
  - no dashboard changes

## Phase 13 - ML Upgrade Sprint 2B (Validation Hardening)

- installed and validated ML runtime dependencies for local experimentation:
  - `scikit-learn`
  - `pyarrow`
  - compatible `pandas` and `numpy`
- upgraded training pipeline with rolling-origin evaluation folds:
  - train to 2005, test 2006-2010
  - train to 2010, test 2011-2015
  - train to 2015, test 2016-2020
  - train to 2020, test 2021-2023
- evaluated model set per indicator:
  - carry-forward baseline
  - linear regression
  - ridge regression
  - random forest regression
- added regional validation outputs:
  - MAE by indicator/model/region
  - report of regions where ML is worse than carry-forward
- added forecast sanity controls:
  - valid value bounds
  - year-to-year jump thresholds
  - null-projection prevention via fallback
  - carry-forward fallback for weak or unstable ML selections
- executed dbt validation builds for Sprint 2 silver models:
  - `silver__ml_structural_risk_panel_country_year`
  - `silver__projection_structural_risk_country_year`
- preserved integration boundaries:
  - no gold scoring integration yet
  - no dashboard integration yet

## Phase 14 - ML Upgrade Sprint 3 (Climate-Only Scenario Integration)

- integrated validated climate ML forecast into gold scenario scoring model:
  - added new scenario `baseline_ml_dynamic_risk`
  - climate uses `coalesce(ml_projection, carry_forward)` fallback logic
- preserved `baseline_static_risk` scenario behavior unchanged
- preserved carry-forward for non-integrated indicators:
  - `vdem_liberal_democracy_index`
  - `adaptation_readiness`
  - `conflict_severity`
- added climate projection metadata fields to scenario output:
  - `climate_vulnerability_projection_source`
  - `climate_vulnerability_forecast_method`
- added projection seed for validated Sprint 2B climate outputs:
  - `ml_climate_vulnerability_projection_2024_2045`
- updated structural-risk projection model to include:
  - static placeholder contract rows
  - ML dynamic climate projection rows
- added scenario validation tests:
  - accepted forecast scenario ids
  - static vs ML country-year forecast coverage parity
- added comparison outputs for impact analysis:
  - `gold__scenario_delta_country_2045`
  - `gold__scenario_delta_summary`
- no dashboard changes

## Phase 15 - ML Upgrade Sprint 4 (Dashboard Scenario Exposure)

- added forecast scenario selector to dashboard forecast views with default:
  - `baseline_static_risk`
  - optional `baseline_ml_dynamic_risk` when available in exported data
- added clear scenario-explanation labels for static vs ML dynamic risk assumptions
- updated dashboard filtering to combine:
  - `historical_observed` rows
  - selected forecast scenario rows
- surfaced climate projection metadata in country view when columns are exported:
  - `climate_vulnerability_projection_source`
  - `climate_vulnerability_forecast_method`
- added scenario comparison section in global overview using optional exports:
  - `scenario_delta_summary`
  - `scenario_delta_country_2045`
- added graceful fallback behavior when comparison files are missing
- updated dashboard export SQL guidance to include:
  - both forecast scenarios in country-score exports
  - optional scenario-delta exports
- documented Sprint 4 delivery in:
  - `docs/ml_forecasting_sprint_4.md`

## Phase 16 - ML Upgrade Sprint 4B (Dashboard Export Refresh and Validation)

- refreshed `dashboard/data` extracts from BigQuery gold models for scenario-aware dashboard behavior
- updated exports to include both forecast scenarios in dashboard-facing tables:
  - `baseline_static_risk`
  - `baseline_ml_dynamic_risk`
- refreshed optional comparison extracts with non-empty data:
  - `scenario_delta_summary.csv`
  - `scenario_delta_country_2045.csv`
- confirmed selector behavior:
  - static baseline remains default
  - ML dynamic risk is available as selectable forecast scenario
- validated loader and page-level data paths for:
  - global overview
  - country explorer
  - regional view
  - scenario comparison section
- attempted local Streamlit smoke test; runtime blocked in sandboxed environment due local socket bind restriction
- documented Sprint 4B refresh and validation results in:
  - `docs/ml_forecasting_sprint_4.md`
