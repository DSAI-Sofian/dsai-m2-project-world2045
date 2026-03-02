# World in 2045 -- Technical Architecture Documentation

## Objective

Build a reproducible, contract-driven data platform to model global
structural trends to 2045.

------------------------------------------------------------------------

## Architecture

### Warehouse

-   Google BigQuery
-   Single dataset routing via environment variable `DBT_DATASET`

### Transformation Layer

-   dbt Core (v1.11+)
-   Schema contracts enforced
-   Generic test arguments updated for 1.11 compliance

------------------------------------------------------------------------

## Conformance Contract

### Grain

(country_iso3, year)

### Canonical Keys

-   country_iso3 (ISO-3166-1 alpha-3)
-   year (INT64)

### Naming Overrides

Custom macros override:

-   generate_schema_name
-   generate_alias_name

Result:

-   silver\_\_\* prefix for conformed models
-   gold\_\_\* prefix for marts

------------------------------------------------------------------------

## Phase 0 Deliverables

-   country_overrides seed
-   dim_country
-   dim_year
-   fact_country_year_spine
-   CI workflow with environment controls

Environment variables:

DBT_TARGET=ci\
DBT_DATASET=world2045_ci

------------------------------------------------------------------------

## Future Phases

Phase 1: - Implement silver\_\_fact_population_country_year - Introduce
WDI/WPP ingestion - Apply partitioning and clustering strategy
