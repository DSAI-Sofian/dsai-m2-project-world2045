# 🌍 World in 2045 -- Data Engineering Blueprint

## Overview

This project answers the question:

**"What will the world look like in 2045?"**

Using a strictly data-driven methodology:

1.  Analyse historical post--World War II data\
2.  Model structural global trends\
3.  Project forward to 2045\
4.  Identify positive growth levers and structural risks

------------------------------------------------------------------------

## Platform Architecture

-   **Google BigQuery** -- Data warehouse\
-   **dbt Core (v1.11+)** -- Transformations and testing\
-   **GitHub Actions** -- Continuous Integration\
-   **Single-dataset convention** -- Controlled via environment variable
    `DBT_DATASET`

------------------------------------------------------------------------

## Logical Data Layers

All project tables live in one dataset and are logically separated by
naming prefix:

  Layer    Prefix
  -------- -------------
  Silver   `silver__*`
  Gold     `gold__*`

Example:

world2045_ci.silver\_\_dim_country\
world2045_ci.silver\_\_fact_country_year_spine\
world2045_ci.gold\_\_mart_world2045_features_country_year

------------------------------------------------------------------------

## Phase 0 -- Foundations (Completed)

-   Implemented ISO3 canonical seed (`country_overrides`)
-   Built `dim_country` and `dim_year`
-   Built `fact_country_year_spine`
-   Enforced dbt contracts + tests
-   Implemented naming macros for dataset routing
-   Configured CI pipeline (dbt deps, seed, build)

------------------------------------------------------------------------

## Running Locally

cd dbt\
dbt deps\
dbt seed --target ci\
dbt build --target ci

------------------------------------------------------------------------

## Next Phase

Phase 1 introduces backbone datasets (WDI, WPP) and first conformed
facts.
