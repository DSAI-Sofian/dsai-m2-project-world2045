# CHANGELOG

## Phase 0 – Platform Initialization

Repository structure created.

Python ingestion framework implemented.

Bronze/Silver/Gold architecture established.

dbt project initialized with BigQuery adapter.

Core warehouse models implemented:

dim_country  
dim_year  
fact_country_year_spine

CI/CD implemented with GitHub Actions validating dbt builds and tests.

---

## Phase 1 – Data Backbone Implementation

Population ingestion pipeline implemented for:

UN World Population Prospects (WPP 2024)

Components created:

run_bronze.py  
WPP ingestion module  
population_standard bronze dataset

Silver model created:

silver__fact_population_country_year

---

World Development Indicators pipeline implemented.

Components created:

wdi.py ingestion module  
API pagination handling  
timeout protection  
indicator filtering

Bronze dataset created:

bronze__wdi_country_year_long

Silver transformation:

silver__wdi_country_year_long

Improvements implemented:

country code normalization  
aggregate removal  
type standardization

---

Country dimension expanded.

Original prototype seed contained:

USA  
SGP

Seed expanded to ~159 sovereign entities.

Models rebuilt:

dim_country  
fact_country_year_spine

---

Gold analytical mart implemented:

gold__mart_world2045_features_country_year

Features integrated:

population  
economic indicators  
health indicators  
technology indicators  
poverty indicators

Mart grain:

country_iso3, year

Coverage indicators added for feature availability.

---

## Phase 1 Final State

Population backbone operational.

Economic indicators integrated.

Country‑year analytical mart implemented.

Total rows in mart:

16059

Coverage:

159 countries  
~101 years

Architecture validated through dbt tests.