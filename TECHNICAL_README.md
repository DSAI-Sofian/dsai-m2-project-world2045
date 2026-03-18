# TECHNICAL README

- [TECHNICAL README](#technical-readme)
  - [Technical purpose](#technical-purpose)
  - [Platform stack](#platform-stack)
  - [Repository design principles](#repository-design-principles)
  - [Warehouse design](#warehouse-design)
  - [Country conformance](#country-conformance)
  - [Core analytical mart](#core-analytical-mart)
  - [Forecast feature mart](#forecast-feature-mart)
  - [Historical trajectory model](#historical-trajectory-model)
  - [Forecast trajectory scenario model](#forecast-trajectory-scenario-model)
  - [Regional aggregation models](#regional-aggregation-models)
  - [Strategic ranking models](#strategic-ranking-models)
  - [Dashboard-ready support marts](#dashboard-ready-support-marts)
  - [Important validation results locked in](#important-validation-results-locked-in)
  - [Indicator Dictionary](#indicator-dictionary)
- [Methodological Limitations and Future Work](#methodological-limitations-and-future-work)
- [Acknowledgements](#acknowledgements)


## Technical purpose

This document records the engineering and analytical design of the World2045 platform. It is written for a technical analyst or data engineer who needs to understand how the repository is organized, how the warehouse is layered, what each model does, and how the analytical outputs were validated.

## Platform stack

- Warehouse: Google BigQuery
- Transformation: dbt
- Scripting: Python
- CI: GitHub Actions
- Version control: Git + GitHub

## Repository design principles

The project was built incrementally with these standing rules:

1. inspect ZIP contents and source schema before proposing ingestion code
2. avoid tests that depend on dbt packages not installed in the repo
3. remain resource-aware for laptop execution
4. validate country-year conformance early
5. separate raw ingestion, standardized facts, and analytical marts

## Warehouse design

**1. Bronze**
Raw-landed or lightly standardized source tables.

Representative examples:

- `bronze__wdi_country_year_long`
- `bronze__wpp_*`
- climate and conflict bronze source tables

**2. Silver**
Conformed country-year facts with normalized keys and consistent field naming.

Representative examples:

- `silver__projection_population_country_year`
- `silver__projection_gdp_country_year_annualized`
- `silver__fact_*_country_year`

**3. Gold**
Wide feature marts and analytical scoring layers.

Critical tables:

- `gold__mart_world2045_features_country_year`
- `gold__forecast_feature_country_year`
- `gold__country_trajectory_score_year`
- `gold__country_trajectory_score_year_scenario`

## Country conformance

Canonical key:

- `country_iso3`

Reference mapping seed:

- `country_overrides`

Important metadata fields in `country_overrides`:

- `iso3`
- `country_name`
- `region`
- `subregion`
- `income_group`
- `is_sovereign`

## Core analytical mart

- `gold__mart_world2045_features_country_year`

This is the principal wide feature mart used for historical analysis.

Important fields used in trajectory work:

- `gdp_per_capita_current_usd`
- `life_expectancy_years`
- `vdem_liberal_democracy_index`
- `adaptation_readiness`
- `climate_vulnerability`
- `battle_deaths`

## Forecast feature mart

- `gold__forecast_feature_country_year`

Constructed from:

- `silver__projection_population_country_year`
- `silver__projection_gdp_country_year_annualized`

Important projected fields:

- `population_total_thousands`
- `life_expectancy_birth_both`
- `gdp_real_billion_usd`
- `gdp_real_per_capita_usd`

## Historical trajectory model

- `gold__country_trajectory_score_year`

Historical trajectory score for 1995-2023.

Normalization approach:

- per-year min-max scaling

Conflict transformation:

- `conflict_severity = ln(1 + battle_deaths)`

Trajectory score formula:

```text
trajectory_score =
  0.30 * gdp_pc_norm
+ 0.25 * life_expectancy_norm
+ 0.20 * governance_norm
+ 0.15 * adaptation_readiness_norm
- 0.10 * climate_vulnerability_norm
- 0.10 * conflict_severity_norm
```

## Forecast trajectory scenario model

- `gold__country_trajectory_score_year_scenario`

This model appends 2024-2045 forecast years to the historical framework.

Scenario design:

- `historical_observed` for 1995-2023
- `baseline_static_risk` for 2024-2045

Projected directly:

- GDP per capita
- life expectancy

Carried forward from latest available historical year:

- governance
- adaptation readiness
- climate vulnerability
- conflict severity

Additional interpretability fields:

- `scenario_id`
- `is_forecast_year`
- `assumption_flag`
- `forecast_score_completeness`

Coverage result locked in during validation:

- complete forecast cases: 150 sovereign/rankable rows in rise-potential layer
- country-level forecast completeness summary from scenario layer: 154 complete countries, 83 partial countries

## Regional aggregation models

- `gold__region_trajectory_score_year`
Region-level aggregation.

- `gold__subregion_trajectory_score_year`
Subregion-level aggregation.

Important implementation note:

A dbt inherited clustering config initially caused failure because the model was created with `cluster by country_iso3`, while the regional output did not include `country_iso3`. The fix was to override clustering at model level.

Recommended filters for interpretability:

- `d.region is not null`
- `d.is_sovereign = true`

## Strategic ranking models

- `gold__country_rise_potential`
Measures strategic position by 2045.

Formula:

```text
rise_potential_score =
  0.50 * trajectory_change_2023_2045
+ 0.35 * trajectory_score_2045
- 0.10 * climate_vulnerability_norm_2023
- 0.05 * conflict_severity_norm_2023
```

- `gold__country_trajectory_momentum`
Measures relative movement / momentum.

Formula:

```text
momentum_score =
  0.70 * trajectory_change_2023_2045
+ 0.20 * trajectory_score_2045
- 0.07 * climate_vulnerability_norm_2023
- 0.03 * conflict_severity_norm_2023
```

- `gold__trajectory_country_quadrant`
2x2 strategic segmentation combining 2045 score and momentum.

Quadrants:

- Future Leaders
- Stable Advanced
- Rising Challengers
- Structural Risk

Final implementation used **median thresholds** for cleaner segmentation.

## Dashboard-ready support marts

- `gold__trajectory_global_year`
- `gold__trajectory_component_breakdown`

These support trend charts, component decomposition charts, and country-level analytical views.

## Important validation results locked in

- Forecast completeness summary: `complete = 154`, `partial = 83`
- Momentum distribution: `very_high = 1`, `moderate = 4`, `low_positive = 67`, `negative = 78`
- Final quadrant distribution: `Future Leaders = 68`, `Structural Risk = 66`, `Rising Challengers = 8`, `Stable Advanced = 8`

## Indicator Dictionary

| Indicator                    | Description                          | Source                    |
| ---------------------------- | ------------------------------------ | ------------------------- |
| population_total             | Total population                     | UN Population Division    |
| gdp_per_capita_current_usd   | GDP per capita in current USD        | World Bank                |
| life_expectancy_years        | Average life expectancy              | World Bank                |
| internet_users_pct           | Percentage of internet users         | World Bank                |
| gini_income                  | Income inequality (Gini coefficient) | World Inequality Database |
| vdem_liberal_democracy_index | Governance and democracy score       | V‑Dem                     |
| climate_vulnerability        | Climate vulnerability index          | ND‑GAIN                   |
| adaptation_readiness         | Climate adaptation readiness         | ND‑GAIN                   |
| battle_deaths                | Conflict battle deaths               | UCDP                      |

---

# Methodological Limitations and Future Work

**Known limitations**

1. forward governance, climate, and conflict are baseline carry-forward rather than projected independently
2. some countries and territories have incomplete historical component coverage
3. regional rollups depend on ISO coverage quality in `country_overrides`
4. normalization is relative by year, so slight negative change may still reflect strong absolute development

---

**Methodological Limitations**

1. Data Coverage Variability
Not all indicators have complete coverage across countries and time periods. Some indicators are unavailable for smaller states or earlier historical years. In such cases, the model relies on interpolation or carry‑forward methods to maintain continuity. This may introduce bias where structural changes occurred but were not captured by the available data.

2. Forecast Assumptions
Forecast extensions from 2024–2045 rely on a combination of projected datasets and carry‑forward assumptions. Governance, climate vulnerability, and conflict indicators are often carried forward from the latest observed year due to limited forward projections. As a result, the forecast scenario represents a **baseline continuation scenario**, not a fully dynamic projection.

3. Indicator Weighting
The trajectory score uses weighted components representing economic, health, governance, climate, and conflict dimensions. While these weights are designed to balance structural development factors, they are ultimately subjective and may influence final rankings. Alternative weighting schemes could yield different outcomes.

4.Normalization Effects
Indicator normalization ensures comparability across variables but can also create relative movement effects. Some countries may appear to decline slightly even if their underlying conditions improve, simply because other countries improve faster.

5. Structural Persistence
Development trajectories often exhibit inertia. The model therefore captures gradual changes rather than abrupt structural shifts. Major geopolitical events, technological disruptions, or policy transformations could alter these trajectories significantly.

---

**Future Work**

Several extensions could enhance the analytical capability of the World2045 platform.

1.Scenario Modeling
Future iterations could incorporate multiple development scenarios, such as:

- optimistic economic growth pathways
- climate transition scenarios
- governance reform trajectories
- conflict risk escalation scenarios

2. Machine Learning Forecasting
Instead of carry‑forward assumptions, machine learning models could generate forward projections for governance, climate resilience, and conflict indicators.

3. Monte Carlo Simulation
Uncertainty ranges could be incorporated using Monte Carlo simulations to produce confidence bands around trajectory scores.

4. Policy Sensitivity Analysis
Future models could estimate how specific policy interventions influence development trajectories.

5. Expanded Indicator Coverage
Additional indicators could improve model robustness, including:

- infrastructure quality
- infrastructure adaptation
- energy transition metrics
- water stress exposure
- technological readiness
- institutional capacity
- food security vulnerability
- ecosystem degradation

---

# Acknowledgements

Portions of the technical design, debugging support, and documentation refinement for this project were assisted by **ChatGPT (OpenAI)**. All final implementation decisions, data engineering work, analytical modeling, and system integration were performed by the project author.
