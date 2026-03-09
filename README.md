# World2045 Data Platform

## Project Objective

Build a multi‑domain analytical platform to study long‑term global
development trends and model plausible trajectories toward the year
2045.

The platform integrates demographic, economic, social, governance, and
risk indicators into a unified **country‑year analytical mart**.

## Architecture

Bronze → Silver → Gold

**Bronze** Raw ingested datasets: - World Development Indicators (WDI) -
UN World Population Prospects (WPP) - V‑Dem Governance Dataset

**Silver** Conformed domain facts and dimensions:

Dimensions - dim_country - dim_year

Spine - fact_country_year_spine

Domain facts - silver\_\_fact_population_country_year -
silver\_\_fact_governance_country_year -
silver\_\_fact_health_country_year -
silver\_\_fact_education_country_year -
silver\_\_fact_inequality_country_year

Indicator transformation - silver\_\_wdi_country_year_long -
silver\_\_wdi_country_year_features

**Gold** Integrated analytical mart

-   gold\_\_mart_world2045_features_country_year
-   gold\_\_mart_world2045_features_analytic_1960_2023

Diagnostics - gold\_\_profile_indicator_coverage_by_year -
gold\_\_profile_indicator_coverage_by_country

## Analytical Window

Dense indicator overlap: 1960 -- 2023

Population projections extend to: 2100

## Current Domain Coverage

Population -- WPP\
Economy -- WDI GDP indicators\
Health -- life expectancy, mortality indicators\
Education -- secondary enrollment\
Inequality -- poverty headcount ratio\
Governance -- V‑Dem indices

## Next Phase

Phase 3 -- Risk Domains

1.  Climate risk
2.  Conflict / geopolitical instability
