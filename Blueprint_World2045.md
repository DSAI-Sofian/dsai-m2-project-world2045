# World in 2045 Data Platform – Expanded Blueprint

## Goal
Build a **country–year analytical platform** to answer:
> What will the world look like in 2045 based on historical trends?

The platform integrates global datasets (population, economic development, health, technology, governance, climate) into a unified **country-year analytical warehouse**.

Grain of the analytical platform:

country_iso3, year

---

# Architectural Overview

The platform follows a modern analytical warehouse pattern.

Bronze → Silver → Gold

Bronze = raw ingestion  
Silver = normalized conformed warehouse  
Gold = analytics marts for modeling and forecasting

---

# Phase 0 – Repository & Platform Foundation

## Objectives
Establish a production‑ready repository and analytics environment.

## Implemented Components

Repository structure:

configs/
data/raw/
scripts/
src/world2045/
tests/
dbt/

CI/CD implemented via GitHub Actions validating:

dbt build  
dbt tests  
repository integrity

Core warehouse foundation:

dim_country  
dim_year  
fact_country_year_spine

Purpose: create the canonical **country‑year backbone** for all datasets.

---

# Phase 1 – Population & WDI Backbone

## Data Sources

UN World Population Prospects (WPP 2024)

World Bank World Development Indicators (WDI)

Minimal indicator set:

GDP (current USD)  
GDP per capita  
GDP growth  
Unemployment rate  
Inflation  
Life expectancy  
Under‑5 mortality  
Secondary school enrollment  
Internet usage  
Electricity access  
Poverty rate  
CO₂ emissions

---

# Bronze Layer

Population ingestion:

scripts/run_bronze.py

Output:

data/raw/wpp2024/population_standard.csv

WDI ingestion:

src/world2045/ingest/wdi.py

Output:

data/raw/wdi/wdi_country_year_long.csv

Structure:

country_id  
year  
indicator_id  
value

---

# Silver Layer

Purpose: normalize all raw sources into conformed warehouse tables.

Dimensions:

silver__dim_country

Canonical ISO‑3166‑1 alpha‑3 dimension derived from:

seeds/country_overrides.csv

Columns include:

country_iso3  
country_name  
region  
income_group

Year dimension:

silver__dim_year

Range:

1945 → 2100

Country‑Year Spine:

silver__fact_country_year_spine

All valid combinations of:

country_iso3, year

This ensures a consistent analytical grain across the warehouse.

Population fact:

silver__fact_population_country_year

Columns:

country_iso3  
year  
population_total

WDI fact:

silver__wdi_country_year_long

Columns:

country_iso3  
year  
indicator_id  
value

Country codes normalized to ISO‑3 via dim_country mapping.

---

# Gold Layer

Analytical mart:

gold__mart_world2045_features_country_year

Purpose:

Provide a unified dataset for forecasting and analytics.

Columns include:

country_iso3  
year

population_total

gdp_current_usd  
gdp_per_capita_current_usd  
gdp_growth_pct  
unemployment_pct  
inflation_cpi_pct

life_expectancy_years  
under5_mortality_rate

secondary_enrollment_pct  
internet_users_pct

access_to_electricity_pct  
poverty_headcount_pct  
co2_emissions_pc

Coverage indicators added for modeling:

population_available  
gdp_available  
life_expectancy_available  
internet_available

---

# Testing Strategy

dbt tests validate:

primary keys  
not-null constraints  
country_iso3 + year uniqueness

---

# Phase 2 – Recommended Expansion

Next datasets to integrate:

Governance (V‑Dem)  
Climate indicators  
Education metrics  
Inequality datasets  
Conflict datasets

All will join to:

fact_country_year_spine

---

# Final Platform Outcome

The platform produces a global **country‑year dataset** enabling:

trend analysis  
country comparisons  
development trajectory analysis  
forecast modeling to 2045