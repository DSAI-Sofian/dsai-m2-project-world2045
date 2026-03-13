# Technical README

- [Technical README](#technical-readme)
  - [1. Environment Setup](#1-environment-setup)
    - [1.1 Python virtual environment](#11-python-virtual-environment)
    - [1.2 BigQuery Dataset](#12-bigquery-dataset)
    - [1.3 Naming Conventions](#13-naming-conventions)
    - [1.4 Partition Strategy](#14-partition-strategy)
    - [1.5 Canonical Keys (Grain)](#15-canonical-keys-grain)
    - [1.6 Known Fixes Applied](#16-known-fixes-applied)
  - [2. Architecture Overview](#2-architecture-overview)
    - [2.1 Core Data Model](#21-core-data-model)
    - [2.2 Country-Year Spine](#22-country-year-spine)
  - [3. Technology Stack](#3-technology-stack)
  - [4. dbt Structure](#4-dbt-structure)
  - [5. Python Ingestion Framework](#5-python-ingestion-framework)
    - [5.1 Ingestion Pattern](#51-ingestion-pattern)
    - [5.2 Scripts](#52-scripts)
  - [6. Development Workflow](#6-development-workflow)
  - [7. Bronze Layer](#7-bronze-layer)
    - [7.1 Current Bronze Outputs](#71-current-bronze-outputs)
  - [8. Silver Layer Models](#8-silver-layer-models)
    - [8.1 Silver Facts](#81-silver-facts)
    - [8.2 Indicator Mapping](#82-indicator-mapping)
    - [8.3 Model Pattern for Indicator-to-Feature Transformation](#83-model-pattern-for-indicator-to-feature-transformation)
  - [9. Gold Layer](#9-gold-layer)
    - [9.1 Primary analytical mart confirmed operational](#91-primary-analytical-mart-confirmed-operational)
    - [9.2 Dense historical dataset for modelling](#92-dense-historical-dataset-for-modelling)
    - [9.3 Diagnostic Models](#93-diagnostic-models)
    - [9.4 Unified analytical dataset combination](#94-unified-analytical-dataset-combination)
  - [10. Ingestion Best Practices](#10-ingestion-best-practices)
    - [10.1 Inspect source files first](#101-inspect-source-files-first)
    - [10.2 Extract minimal columns](#102-extract-minimal-columns)
    - [10.3 Avoid high memory loads](#103-avoid-high-memory-loads)
    - [10.4 Validate schema before dbt](#104-validate-schema-before-dbt)
  - [11. dbt Testing Strategy](#11-dbt-testing-strategy)
    - [11.1 Tests implemented](#111-tests-implemented)
  - [12. Future Technical Enhancements](#12-future-technical-enhancements)

---

## 1. Environment Setup

### 1.1 Python virtual environment

* python -m venv .venv
* source .venv/bin/activate

Install dbt

* pip install "dbt-core==1.11.*" "dbt-bigquery==1.11.*"

dbt Profiles

* profiles.yml must contain profile:
  * world2045

* Dataset controlled via environment variable:
  * export DBT_DATASET=world2045_ci

### 1.2 BigQuery Dataset

* Dataset location: US
* Dataset: world2045_ci

### 1.3 Naming Conventions

* Table naming pattern:
  * layer__entity

* Examples:
  * silver__fact_population_country_year
  * gold__mart_world2045_features_country_year

### 1.4 Partition Strategy

* Large fact tables partitioned by:
  -year

* Clustered by:
  * country_iso3

### 1.5 Canonical Keys (Grain)

* country_iso3
* year

### 1.6 Known Fixes Applied

* Resolved double-prefix naming caused by generate_alias_name macro.

---

## 2. Architecture Overview

The World2045 platform uses a layered data architecture.

Layer | Description
---|---
Bronze | Raw ingested datasets
Silver | Cleaned and conformed datasets
Gold | Analytical marts and modeling inputs

### 2.1 Core Data Model

**Dimension Tables**

dim_country

**Canonical country dimension using **ISO-3166-1 alpha-3 codes**.

Key column:

```
country_iso3
```

**Calendar year dimension**

Coverage:

```
1945 → 2100
```

### 2.2 Country-Year Spine

```
fact_country_year_spine
```

This table contains **all valid country-year combinations**.

Purpose:

* ensures consistent joins
* guarantees analytical grain
* prevents missing entity-year combinations

All facts must join through the spine.

---

## 3. Technology Stack

| Component       | Technology      |
| --------------- | --------------- |
| Warehouse       | Google BigQuery |
| Transformation  | dbt             |
| Ingestion       | Python          |
| Version Control | GitHub          |
| CI              | GitHub Actions  |

---

## 4. dbt Structure

```
models/

bronze/  
silver/  
  dims/  
  facts/  
gold/

seeds/

country_overrides.csv
```

---

## 5. Python Ingestion Framework

```
src/world2045/
  ingest/
    run_bronze.py
    wpp.py
    wdi.py
  loaders/
    bigquery.py
  quality/
    checks.py
  utils/
    io.py
    paths.py
```

### 5.1 Ingestion Pattern

1. Extract raw data
2. Validate schema
3. Save normalized raw files
4. Load to Bronze tables

### 5.2 Scripts

* Run ingestion pipelines
  * run_bronze.py

* Load CSV outputs to BigQuery tables
  * load_bronze_bigquery.py

---

## 6. Development Workflow

Run ingestion:

```
python scripts/run_bronze.py
```

Load to BigQuery:

```
python scripts/load_bronze_bigquery.py
```

Build warehouse:

```
cd dbt
dbt build
```

---

## 7. Bronze Layer

Source | Purpose
---|---
UN World Population Prospects 2024 | population backbone
World Development Indicators | economic and social indicators

### 7.1 Current Bronze Outputs

Dataset | Location
---|---
WPP2024 population | `data/raw/wpp2024`
WDI placeholder | `data/raw/wdi/wdi_country_year_long.csv`
*To add more from repo table*

All future datasets attach to:

```
fact_country_year_spine
```

Purpose:

* ensures consistent joins
* guarantees analytical grain
* prevents missing entity-year combinations

All facts must join through the spine.

---

## 8. Silver Layer Models

### 8.1 Silver Facts

| Model       | Source      |
| --------------- | --------------- |
| silver__fact_population_country_year | UN World Population Prospects |
| silver__fact_health_country_year | UN World Population Prospects |
| silver__fact_education_country_year | UN World Population Prospects |
| silver__fact_inequality_country_year | UN World Population Prospects |
| silver__fact_climate_risk_country_year | UN World Population Prospects |
| silver__fact_conflict_country_year | UN World Population Prospects |
| silver__fact_hdi_country_year | UN World Population Prospects |
| silver__fact_hdi_country_year_annualized | UN World Population Prospects |

### 8.2 Indicator Mapping

Refer to the following documents for details:

* World2045_Master_Indicator_Map
* World2045_dbt_indicator_mapping

### 8.3 Model Pattern for Indicator-to-Feature Transformation

Refer to the following documents for details:

* World2045_dbt_model_pattern.md

---

## 9. Gold Layer

### 9.1 Primary analytical mart confirmed operational

`gold__mart_world2045_features_country_year`

* Integrated country‑year analytical feature table

### 9.2 Dense historical dataset for modelling

`gold__mart_world2045_features_analytic_1960_2023`

### 9.3 Diagnostic Models

`gold__mart_profile_indicator_coverage_by_year`

* Tracks indicator density over time

`gold__mart_profile_indicator_coverage_by_country`

* Tracks data completeness per country

`gold__features_world2045_normalized_country_year`

* Normalized Layer

`gold__mart_world2045_model_dataset`

* Model Dataset

### 9.4 Unified analytical dataset combination

```
population
economic indicators
social indicators
development trajectories
inequality concentration
governance dynamics
climate vulnerability
conflict exposure
```

Example columns:

```
population_total
gdp_current_usd
life_expectancy_years
internet_users_pct
vdem_liberal_democracy_index
```

Availability flags are generated for each major domain.

Example:

```
population_available
gdp_available
governance_available
```

The final modeling panel contains:

- 159 countries
- 96 years (1950 - 2045)
- 15,264 rows

---

## 10. Ingestion Best Practices

The following rules are applied for all ingestion pipelines.

### 10.1 Inspect source files first

Always inspect source ZIP contents before building ingestion scripts.

### 10.2 Extract minimal columns

Wide datasets should first be narrowed before loading.

### 10.3 Avoid high memory loads

Large files should be streamed or filtered before ingestion.

### 10.4 Validate schema before dbt

Bronze files must be verified before building silver models.

---

## 11. dbt Testing Strategy

Basic unit tests exist for:

* path utilities
* quality checks

Run with:

```
pytest
```

### 11.1 Tests implemented

**Column integrity**

```
not_null
```

**Referential integrity**

```
relationships
```

**Analytical grain**

```
dbt_utils.unique_combination_of_columns
```

**CI Pipeline**

GitHub Actions runs dbt checks automatically via:

```
.github/workflows/dbt-ci.yml
```

Actions execute:

```
dbt deps
dbt seed
dbt build
```

This ensures all models compile and pass tests.

---

## 12. Future Technical Enhancements

Planned improvements:

* partitioning and clustering for BigQuery tables
* domain-specific marts
* data quality monitoring
* feature store for predictive modelling

---
