# World in 2045 — Technical Documentation

## Technology Stack

| Component       | Technology      |
| --------------- | --------------- |
| Warehouse       | Google BigQuery |
| Transformation  | dbt             |
| Ingestion       | Python          |
| Version Control | GitHub          |
| CI              | GitHub Actions  |

---

# Warehouse Dataset

```
world2045_ci
```

All models are materialized in a **single dataset architecture**.

Example table names:

```
silver__fact_population_country_year
silver__wdi_country_year_long
gold__mart_world2045_features_country_year
```

---

# Core Data Model

## Dimension Tables

### dim_country

Canonical country dimension using **ISO-3166-1 alpha-3 codes**.

Key column:

```
country_iso3
```

Additional attributes:

* region
* subregion
* income_group

---

### dim_year

Calendar year dimension.

Coverage:

```
1945 → 2100
```

---

# Country-Year Spine

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

# Silver Layer Models

### Population

```
silver__fact_population_country_year
```

Source:

```
UN World Population Prospects
```

Grain:

```
country_iso3, year
```

---

### WDI Indicators

```
silver__wdi_country_year_long
```

Structure:

```
country_iso3
year
indicator_id
value
```

This long format allows flexible pivoting of indicators.

---

### Governance (V-Dem)

```
silver__fact_governance_country_year
```

Indicators:

```
vdem_liberal_democracy_index
vdem_electoral_democracy_index
vdem_judicial_constraints_index
vdem_civil_liberties_index
```

---

# Gold Layer

### mart_world2045_features_country_year

Unified analytical dataset combining:

```
population
economic indicators
social indicators
governance indicators
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

---

# dbt Testing Strategy

Tests implemented:

### Column integrity

```
not_null
```

### Referential integrity

```
relationships
```

### Analytical grain

```
dbt_utils.unique_combination_of_columns
```

---

# Ingestion Best Practices

The following rules are applied for all ingestion pipelines.

### 1 Inspect source files first

Always inspect source ZIP contents before building ingestion scripts.

### 2 Extract minimal columns

Wide datasets should first be narrowed before loading.

### 3 Avoid high memory loads

Large files should be streamed or filtered before ingestion.

### 4 Validate schema before dbt

Bronze files must be verified before building silver models.

---

# CI Pipeline

GitHub Actions executes:

```
dbt deps
dbt seed
dbt build
```

This ensures all models compile and pass tests.

---

# Future Technical Enhancements

Planned improvements:

* partitioning and clustering for BigQuery tables
* domain-specific marts
* data quality monitoring
* feature store for predictive modelling

---
