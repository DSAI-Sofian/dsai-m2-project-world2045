# CHANGELOG

## Phase 2 — Governance Integration

Major milestone introducing governance indicators.

### Added

* V-Dem dataset ingestion pipeline
* `silver__fact_governance_country_year` model
* governance indicators added to gold mart

Indicators included:

* liberal democracy index
* electoral democracy index
* judicial constraints index
* civil liberties index

### Improvements

* governance availability flags in gold mart
* validation tests for country and year keys
* standardized governance schema

### Fixes

* corrected population reference in gold mart
* resolved dbt naming mismatch between logical and physical tables
* removed unsupported `dbt_expectations` tests

---

## Phase 1 — Development Backbone

### Added

* UN population ingestion
* World Bank WDI ingestion
* country-year conformed schema

### New tables

```
dim_country
dim_year
fact_country_year_spine
silver__fact_population_country_year
silver__wdi_country_year_long
```

### Gold mart

Initial version of:

```
mart_world2045_features_country_year
```

with economic and social indicators.

---

## Phase 0 — Infrastructure Setup

### Repository initialization

* project directory structure
* Python ingestion framework

### Warehouse

* BigQuery dataset
* dbt project configuration

### CI

* GitHub Actions dbt pipeline

---
