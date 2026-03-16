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
