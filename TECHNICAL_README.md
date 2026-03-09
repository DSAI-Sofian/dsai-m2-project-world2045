# Technical README -- World2045 Platform

## Technology Stack

-   BigQuery
-   dbt (v1.11)
-   Python ingestion scripts
-   GitHub CI

## Warehouse Design

Single dataset strategy.

Tables are prefixed by layer:

silver\_\_\* gold\_\_\*

### Grain

Primary analytical grain:

country_iso3 + year

## Key Tables

### Population

silver\_\_fact_population_country_year

Source: UN WPP

Coverage: 1950 -- 2100

### Governance

silver\_\_fact_governance_country_year

Source: V‑Dem

### WDI Long Table

silver\_\_wdi_country_year_long

Structure:

country_iso3\
year\
indicator_id\
value

## Domain Fact Models

Health

Indicators: SP.DYN.LE00.IN -- life expectancy\
SH.DYN.MORT -- under‑5 mortality

Education

Indicator: SE.SEC.ENRR -- secondary enrollment

Inequality

Indicator: SI.POV.LMIC -- poverty headcount

## Gold Mart

gold\_\_mart_world2045_features_country_year

Purpose: Integrated country‑year analytical feature table.

### Analytic Slice

gold\_\_mart_world2045_features_analytic_1960_2023

Purpose: Dense historical dataset for modelling.

## Diagnostic Models

gold\_\_profile_indicator_coverage_by_year

Tracks indicator density over time.

gold\_\_profile_indicator_coverage_by_country

Tracks data completeness per country.
