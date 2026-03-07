# World in 2045 — Global Development Data Platform

## Project Objective

The **World in 2045** project builds a structured analytical data platform designed to explore historical global development trends and support long-range analysis of the world approaching the year **2045**.

The platform integrates data from international statistical organizations such as:

* United Nations Population Division
* World Bank World Development Indicators (WDI)
* V-Dem Institute Governance Dataset
* (Planned) WHO Global Health Observatory
* (Planned) Climate and conflict datasets

The final outcome is a **country-year analytical warehouse** capable of supporting:

* historical trend analysis
* comparative country analysis
* development trajectory modelling
* long-term scenario analysis

---

# Analytical Grain

All data in the warehouse conforms to a single analytical grain:

```
country_iso3
year
```

Example row:

| country | year | population | gdp | democracy_index | life_expectancy |
| ------- | ---- | ---------- | --- | --------------- | --------------- |
| SGP     | 2020 | ...        | ... | ...             | ...             |

---

# Key Business Questions

The platform enables analysis of questions such as:

### Development Trajectory

* Which countries are improving most rapidly in governance, education and economic indicators?
* What patterns precede sustained development?

### Governance & Stability

* Does democratic governance correlate with long-term economic growth?
* Are judicial independence and civil liberties predictive of prosperity?

### Population & Economy

* How do demographic changes affect economic development?
* Which countries are approaching demographic decline?

### Digital Development

* How does internet penetration relate to GDP growth and education?

### Future Outlook

* Which countries are likely to achieve high-income status by **2045**?

---

# Platform Architecture

The warehouse follows a **modern ELT layered architecture**.

```
Raw Data Sources
       ↓
Bronze Layer
(raw ingestion)
       ↓
Silver Layer
(conformed normalized warehouse)
       ↓
Gold Layer
(analytical feature marts)
```

### Bronze

Raw datasets ingested from source systems.

Examples:

* UN Population Division (WPP)
* World Bank WDI
* V-Dem Governance Dataset

### Silver

Conformed warehouse tables standardized to the **country-year grain**.

Key tables:

```
dim_country
dim_year
fact_country_year_spine
silver__fact_population_country_year
silver__wdi_country_year_long
silver__fact_governance_country_year
```

### Gold

Analytical marts used for modeling and exploration.

Primary mart:

```
mart_world2045_features_country_year
```

This mart integrates:

* population
* economic indicators
* development indicators
* governance indicators

---

# Indicators Currently Included (Phase 2)

### Population

* total population

### Economy

* GDP current USD
* GDP per capita
* GDP growth

### Social Indicators

* life expectancy
* under-5 mortality
* internet penetration
* electricity access
* secondary school enrollment
* poverty headcount

### Governance (V-Dem)

* liberal democracy index
* electoral democracy index
* judicial constraints index
* civil liberties index

---

# Data Testing Strategy

Data validation is implemented using **dbt tests**.

Key validation rules:

### Key integrity

```
country_iso3 not_null
year not_null
```

### Referential integrity

```
relationships → dim_country
relationships → dim_year
```

### Analytical grain validation

```
unique(country_iso3, year)
```

These guarantees ensure every dataset conforms to the **country-year analytical schema**.

---

# Repository Structure

```
dsai-m2-personal-assignment/

src/world2045/
    ingest/
    utils/

dbt/
    models/
        silver/
        gold/
    seeds/
    tests/

data/
    raw/
    bronze/
```

---

# Project Phases

### Phase 0 — Infrastructure

* repository structure
* dbt project initialization
* BigQuery warehouse
* CI pipeline

### Phase 1 — Core Development Data

* UN population ingestion
* WDI ingestion
* country-year warehouse backbone

### Phase 2 — Governance

* V-Dem governance ingestion
* governance feature integration

Future phases will introduce:

* education
* health
* climate risk
* inequality
* conflict indicators

---

# Current Status

Completed phases:

```
Phase 0 — Infrastructure
Phase 1 — Population & Economic Backbone
Phase 2 — Governance Indicators
```

The platform now provides a unified dataset capable of supporting multi-domain development analysis.

---
