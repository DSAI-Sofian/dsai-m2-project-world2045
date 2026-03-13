# CHANGELOG

## Phase 0 Development - 04.03.2026 & 05.03.2026

### Platform Initialization

- Python ingestion framework implemented
- Bronze/Silver/Gold architecture established
- dbt project initialized with BigQuery adapter
- Core warehouse models implemented
- CI/CD implemented with GitHub Actions validating dbt builds and tests

### Fixed

- dbt profile misconfiguration
- GitHub CI YAML syntax errors
- dbt dependency installation issues
- BigQuery header incompatibility
- dbt alias macro double prefix bug

### Infrastructure

- BigQuery dataset configured
- dbt incremental merge strategy implemented
- Partitioning by year
- Clustering by country_iso3
- Models built:
  - dim_country  
  - fact_country_year_spine

## Phase 0 Implementation - 06.03.2026 & 07.03.2026

### Data Backbone Implementation

- Production‑grade repository structure
- Python ingestion framework (`src/world2045`)
- Bronze ingestion runner (`scripts/run_bronze.py`)
- Utility modules:
  - paths
  - io
  - quality checks
- pyproject.toml for Python package configuration

### Data

- Population ingestion pipeline implemented
  - Added WPP2024 raw dataset
  - Generated standardized population CSV
- Prototype seed contained:
  - USA  
  - SGP

### Testing

Validated pipeline with:

```
pytest
python scripts/run_bronze.py
```

## Phase 1 Development - 09.03.2026

- World Development Indicators pipeline implemented
  - Components created:
    - wdi.py ingestion module  
    - API pagination handling  
    - timeout protection  
    - indicator filtering
- Bronze dataset created:
  - bronze__wdi_country_year_long
- Silver transformation:
  - silver__fact_population_country_year
  - silver__wdi_country_year_long

### Improvements implemented

- Country code normalization  
- Aggregate removal  
- Type standardization
- Country dimension expanded
  - Seed expanded to ~159 sovereign entities.

### Data Pipeline Fixes

- Corrected ingestion of **UN World Population Prospects 2024** datasets.
- Resolved CSV metadata header issues (`skiprows=16`).
- Cleaned column names to satisfy BigQuery field naming constraints.
- Introduced cleaned ingestion sources (`wpp2024_f01_sheet*_clean`).

### Warehouse Changes

- Bronze tables successfully loaded to BigQuery:
  - `bronze__wpp2024__f01_sheet1_clean`
  - `bronze__wpp2024__f01_sheet2_clean`
  - `bronze__wpp2024__population_standard`
- Rebuilt population fact model:
  - `silver__fact_population_country_year`

### Coverage Validation

- Population coverage confirmed: **1950–2100**
- Analytical overlap across GDP / Life Expectancy / Population:
  - **1960–2023**

## Phase 1 Development (continued) - 10.03.2026

- Gold analytical mart implemented
  - Features integrated:
    - Population  
    - Economic indicators  
    - Health indicators  
    - Technology indicators  
    - Poverty indicators
- Mart grain:
  - country_iso3
  - year
- Coverage indicators added for feature availability

## Phase 1 Final State

- Population backbone operational
- Economic indicators integrated
- Country‑year analytical mart implemented
- Total rows in mart - 16059
- Coverage - 159 countries, ~101 years
- Architecture validated through dbt Util tests.

---

## Phase 2 Development - 10.03.2026 & 11.03.2026

### Governance, Climate & Conflict Integration

- V-Dem dataset ingestion pipeline
- governance indicators added to gold mart
  - liberal democracy index
  - electoral democracy index
  - judicial constraints index
  - civil liberties index
- Added Climate domain (ND‑GAIN datasets)
- Added Conflict domain (UCDP datasets)
- Gold mart extended with climate and conflict indicators

### Improvements

- Governance availability flags in gold mart
- Validation tests for country and year keys
- Standardized governance schema

### Fixes

- Corrected population reference in gold mart
- Resolved dbt naming mismatch between logical and physical tables

### Socio‑Economic Domain Expansion

- Added health domain model silver
- Added education domain model silver
- Added inequality domain model silver
- Aligned models with actual WDI indicators present in dataset

### Gold Mart Enhancements

- Updated gold features mart
- Added availability flags
- Created gold analytical slice
- Added Data completeness diagnostics for modelling readiness

### Human Development Index & World Inequality Data Integration

- HDI ingestion pipeline and cleaning script
- Added HDI domain model silver
- Added HDI Annualization Policy (refer to TECHNICAL_README.MD)
- WID inequality indicators

## Phase 3 Development - 12.03.2026

### Analytical Layer Development

- Model Dataset Specification
  - Normalized features:
    - hdi_zscore  
    - gini_income_zscore  
    - bottom50_income_share_pct_zscore  
    - top10_income_share_pct_zscore  
    - top1_income_share_pct_zscore  
  - Metadata:
    - non_null_feature_count  
    - is_model_usable  
    - is_training_usable  
    - is_scoring_usable  
  - Panel segmentation:
    - pre_hdi_period (1950–1989)  
    - train_observed_period (1990–2023)  
    - forecast_period (2024–2045)
