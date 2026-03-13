# World in 2045 Blueprint

## Goal
Answer: **“What the world looks like in 2045”** using a strictly **data-driven** approach.

### Approach
1. Analyze past data (post–World War 2)
2. Extrapolate historical trends to predict future development
3. Develop a snapshot of the world in 2045
4. Propose actions to encourage positive growth and remediate negative trajectories

---

# Official Scope of Analysis

## Core Dimensions
1. Population growth (country-level, multiple metrics)
2. Social, political, and governmental development
3. Quality of life
4. Mortality and health outcomes
5. Cost of living and macroeconomic stability
6. Technological growth across sectors
7. Inequality (income and wealth)

## Additional Dimensions (Now Included in Official Scope)
8. Climate and environmental risk
9. Conflict and geopolitical stability
10. Education and human capital
11. Labor market structure and productivity

### Requirement
- **All analysis and predictions must be empirically grounded in historical data.**

---

# Public Data Sources (by domain)

## Population & Demographics
- UN World Population Prospects (WPP)
- World Bank World Development Indicators (WDI)

## Governance & Political Development
- V-Dem
- Polity Project
- Worldwide Governance Indicators (WGI)

## Quality of Life
- UNDP Human Development Index (HDI)
- World Happiness Report / Gallup outputs

## Mortality & Health
- WHO Global Health Observatory
- IHME Global Burden of Disease (GBD)

## Cost of Living & Macroeconomics
- IMF World Economic Outlook (WEO)
- OECD Data

## Technology & Innovation
- ITU ICT statistics
- WIPO patent and innovation data

## Inequality
- World Inequality Database (WID)

## Climate & Environment
- UNFCCC emissions datasets
- NASA GISS temperature anomalies
- Climate risk indices (e.g., Germanwatch)

## Conflict & Security
- Uppsala Conflict Data Program (UCDP)
- SIPRI military expenditure database

## Education & Human Capital
- UNESCO Institute for Statistics
- OECD PISA

## Labor Market
- ILOSTAT

---

# Target Data Architecture (Google Cloud)

## Core Platform Components
- **Cloud Storage (GCS)** – raw immutable landing (bronze files)
- **BigQuery** – warehouse (single-dataset convention for this project)
- **Cloud Run / Cloud Functions** – ingestion jobs
- **Cloud Scheduler** – orchestration triggers
- **dbt (Core or Cloud)** – transformation, modeling, testing
- **GitHub Actions** – CI for dbt build/test

## Single-Dataset Convention (Confirmed)
All project relations live inside a single BigQuery dataset (CI: `world2045_ci`; dev/prod set via environment variables), using logical layer prefixes:
- `silver__*` for conformed models (dims/facts)
- `gold__*` for marts

Dataset selection is controlled by environment variable:
- `DBT_DATASET` (falls back to `target.dataset` when unset)

---

# ELT Workflow (Recommended)

## Rationale for ELT on GCP
- BigQuery optimized for large-scale SQL transformations
- Raw data preserved for audit and reproducibility
- Schema evolution handled downstream
- Reduced pipeline fragility compared to heavy ETL preprocessing

## Workflow Stages

### 1. Extract
- API pull or bulk download
- Store raw payload in GCS with versioning

### 2. Load
- Load raw files into BigQuery bronze tables
- Minimal typing and transformation
- Add metadata columns:
  - ingested_at
  - source_release
  - source_file

### 3. Transform
- dbt-managed SQL transformations
- Conform to country-year grain
- Standardize units, currencies, inflation adjustments
- Build feature sets for projection models


## Rationale for ELT on GCP
- BigQuery optimized for large-scale SQL transformations
- Raw data preserved for audit and reproducibility
- Schema evolution handled downstream
- Reduced pipeline fragility compared to heavy ETL preprocessing

## Workflow Stages

### 1. Extract
- API pull or bulk download
- Store raw payload in GCS with versioning

### 2. Load
- Load raw files into BigQuery bronze tables
- Minimal typing and transformation
- Add metadata columns:
  - ingested_at
  - source_release
  - source_file

### 3. Transform
- dbt-managed SQL transformations
- Conform to country-year grain
- Standardize units, currencies, inflation adjustments
- Build feature sets for projection models

---

# Dataset Priority List (Ingestion Order)

## Phase 0 – Foundations
- dim_country (ISO-3 standardized mapping)
- dim_year (post-1945 coverage)
- Metadata registry

## Phase 1 – Backbone Datasets
1. World Bank WDI
2. UN WPP
3. WHO GHO
4. UNDP HDI

Deliverable: Working country-year panel with demographic + economic + health baseline.

## Phase 2 – Governance
1. V-Dem
2. WGI
3. Polity

Deliverable: Governance feature pack.

## Phase 3 – Macro Stability & Inequality
1. WID
2. IMF WEO
3. OECD

Deliverable: Inequality + macro volatility indicators.

## Phase 4 – Technology
1. ITU
2. WIPO

Deliverable: Tech adoption and innovation metrics.

## Phase 5 – Risk & Structural Drivers
1. Climate datasets
2. Conflict datasets
3. Education datasets
4. Labor datasets

Deliverable: Scenario-driving structural variables.

---

# Table Naming Conventions (BigQuery)

## Layered Datasets
- bronze_<source>
- silver_conformed
- gold_marts

## Dimension Tables
- dim_country
- dim_year

## Fact Tables (Silver)
- fact_population_country_year
- fact_health_country_year
- fact_governance_country_year
- fact_economy_country_year
- fact_tech_country_year
- fact_inequality_country_year
- fact_climate_country_year
- fact_conflict_country_year
- fact_education_country_year
- fact_labor_country_year

## Gold Marts
- mart_world2045_features_country_year
- mart_world2045_snapshot_2045
- mart_world2045_scenarios

---

# Conformance (Country–Year Transformation Contract)

## Grain
- Primary grain: **country_iso3 × year**
- Every silver fact table must be **unique** on `(country_iso3, year)` (plus optional sub-dimension keys if introduced later).

## Canonical Keys
### Country
- Canonical key: `country_iso3` (**ISO-3166-1 alpha-3**)
- Maintain a country mapping dimension and (when needed) bridge tables to handle:
  - Alternate codes across publishers
  - Historical entities / splits / merges
  - Disputed territories (explicit flags)

### Time
- Canonical key: `year` (INT64, calendar year)
- Sources with multi-year periods/surveys keep original period in bronze; silver maps to:
  - `year` (reference year)
  - Optional `period_type`, `period_start_year`, `period_end_year` when material

## Units, Rates, Currency
- Make units explicit in column naming and/or metadata:
  - Percent as `*_pct` (0–100)
  - Rates as `*_per_100`, `*_per_1000`, `*_per_100k` (explicit denominator)
- Currency normalization (for cross-country comparability):
  - `*_constant_usd` with base-year defined in metadata
  - `*_ppp_constant` where applicable

## Silver Dataset Layout (BigQuery)
Dataset: `silver_conformed`
- Dimensions: `dim_country`, `dim_year`
- Domain facts:
  - `fact_population_country_year`
  - `fact_health_country_year`
  - `fact_economy_country_year`
  - `fact_cost_country_year` (optional; merge into economy if coverage limited)
  - `fact_governance_country_year`
  - `fact_inequality_country_year`
  - `fact_tech_country_year`
  - `fact_climate_country_year`
  - `fact_conflict_country_year`
  - `fact_education_country_year`
  - `fact_labor_country_year`
- Unified wide table for modeling (recommended): `fact_country_year_core`

## Common Provenance Columns (every silver fact)
- `source_system`, `source_dataset`, `source_release`, `source_indicator_id`
- `source_unit`, `source_freq`
- `ingested_at`, `transformed_at`, `row_hash`

## Column-level Domain Schemas
- Population: `population_total`, `urbanization_rate_pct`, `fertility_rate_births_per_woman`, `crude_birth_rate_per_1000`, `crude_death_rate_per_1000`, `net_migration_per_1000`, `median_age_years`, `dependency_ratio_pct`, etc.
- Health: `life_expectancy_years`, `hale_years`, `infant_mortality_per_1000`, `under5_mortality_per_1000`, `maternal_mortality_per_100k`, `health_expenditure_pct_gdp`, etc.
- Economy: `gdp_constant_usd`, `gdp_per_capita_constant`, `gdp_growth_pct`, `inflation_cpi_pct`, `gov_debt_pct_gdp`, etc.
- Governance: `vdem_libdem_index`, `polity2_score`, `wgi_rule_of_law`, `wgi_control_corruption`, etc.
- Inequality: `gini_income`, `top1_income_share_pct`, `top10_income_share_pct`, `bottom50_income_share_pct`, etc.
- Tech: `internet_users_pct`, `mobile_subscriptions_per_100`, `fixed_broadband_per_100`, `r_and_d_pct_gdp`, `patents_resident_per_million`, etc.
- Climate: `co2_emissions_total_mt`, `co2_per_capita_t`, `renewable_energy_share_pct`, `climate_risk_index`, etc.
- Conflict: `conflict_events_count`, `conflict_fatalities`, `military_expenditure_pct_gdp`, etc.
- Education: `literacy_rate_pct`, `mean_years_schooling`, `expected_years_schooling`, `pisa_math_score`, etc.
- Labor: `labor_force_participation_pct`, `employment_to_population_pct`, `youth_unemployment_pct`, `informal_employment_pct`, etc.

## Gold Modeling Mart Contract
- `mart_world2045_features_country_year` is built from conformed silver facts.
- `fact_country_year_core` is the preferred “wide” modeling table for feature generation.

---

# dbt Test Suite Strategy

## Structural Tests
- Primary key uniqueness (country_iso3 + year)
- Not-null constraints on keys
- Referential integrity (facts → dim_country, dim_year)

## Domain Tests
- Accepted value ranges (e.g., democracy index bounds)
- Non-negative constraints (population, GDP)
- Logical checks (life expectancy < 120)

## Temporal Consistency Tests
- Detect extreme year-over-year jumps
- Outlier detection flags

## Coverage Diagnostics
- Missingness heatmaps (country vs year)
- Indicator coverage percentage

---

# Modeling Direction (Preview)

- Panel regression with fixed effects
- Structural time series (trend + shock decomposition)
- Bayesian scenario modeling
- Monte Carlo uncertainty bands
- Cohort-component demographic modeling

This blueprint will continue to evolve as ingestion stabilizes and modeling design matures.

