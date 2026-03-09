# World2045 dbt Model Pattern for Indicator-to-Feature Transformation

## Purpose

This pattern provides a compact, reusable dbt approach for transforming selected indicators
from a long-format source table into a wide feature model suitable for the gold mart.

It is designed for the existing World2045 warehouse architecture:

- `silver__wdi_country_year_long`
- `country_iso3`
- `year`
- selected indicators pivoted into explicit feature columns

---

## Recommended Input Assumptions

Source table:

```sql
silver__wdi_country_year_long
```

Expected columns:

```text
country_iso3
year
indicator_id
indicator_name
indicator_value
```

---

## Minimal dbt Model Pattern

Suggested model name:

```text
silver__wdi_country_year_features.sql
```

```sql
{{ config(
    materialized="table",
    partition_by={
      "field": "year",
      "data_type": "int64",
      "range": {"start": 1950, "end": 2101, "interval": 1}
    },
    cluster_by=["country_iso3"]
) }}

with src as (

    select
        country_iso3,
        cast(year as int64) as year,
        indicator_id,
        cast(indicator_value as float64) as indicator_value
    from {{ ref('silver__wdi_country_year_long') }}
    where indicator_id in (
        'NY.GDP.PCAP.CD',
        'NY.GDP.MKTP.KD.ZG',
        'FP.CPI.TOTL.ZG',
        'SL.UEM.TOTL.ZS',
        'NE.GDI.TOTL.ZS',
        'SE.SEC.ENRR',
        'SE.ADT.LITR.ZS',
        'SH.XPD.CHEX.GD.ZS',
        'SP.DYN.IMRT.IN',
        'SH.MED.PHYS.ZS',
        'SI.POV.GINI',
        'SI.POV.DDAY',
        'SP.URB.TOTL.IN.ZS',
        'SL.UEM.1524.ZS',
        'SP.POP.DPND'
    )

),

pivoted as (

    select
        country_iso3,
        year,

        max(case when indicator_id = 'NY.GDP.PCAP.CD' then indicator_value end) as gdp_per_capita_current_usd,
        max(case when indicator_id = 'NY.GDP.MKTP.KD.ZG' then indicator_value end) as gdp_growth_pct,
        max(case when indicator_id = 'FP.CPI.TOTL.ZG' then indicator_value end) as inflation_cpi_pct,
        max(case when indicator_id = 'SL.UEM.TOTL.ZS' then indicator_value end) as unemployment_pct,
        max(case when indicator_id = 'NE.GDI.TOTL.ZS' then indicator_value end) as investment_pct_gdp,

        max(case when indicator_id = 'SE.SEC.ENRR' then indicator_value end) as secondary_enrollment_pct,
        max(case when indicator_id = 'SE.ADT.LITR.ZS' then indicator_value end) as literacy_rate_pct,
        max(case when indicator_id = 'SH.XPD.CHEX.GD.ZS' then indicator_value end) as health_expenditure_pct_gdp,
        max(case when indicator_id = 'SP.DYN.IMRT.IN' then indicator_value end) as infant_mortality_per_1000,
        max(case when indicator_id = 'SH.MED.PHYS.ZS' then indicator_value end) as physicians_per_1000,

        max(case when indicator_id = 'SI.POV.GINI' then indicator_value end) as gini_income,
        max(case when indicator_id = 'SI.POV.DDAY' then indicator_value end) as poverty_headcount_pct,
        max(case when indicator_id = 'SP.URB.TOTL.IN.ZS' then indicator_value end) as urban_population_pct,
        max(case when indicator_id = 'SL.UEM.1524.ZS' then indicator_value end) as youth_unemployment_pct,
        max(case when indicator_id = 'SP.POP.DPND' then indicator_value end) as dependency_ratio_pct

    from src
    group by country_iso3, year

)

select * from pivoted
```

---

## Recommended Gold-Mart Join Pattern

Suggested use inside:

```text
gold__mart_world2045_features_country_year.sql
```

```sql
with spine as (

    select * from {{ ref('silver__fact_country_year_spine') }}

),

population as (

    select * from {{ ref('silver__fact_population_country_year') }}

),

governance as (

    select * from {{ ref('silver__fact_governance_country_year') }}

),

wdi_features as (

    select * from {{ ref('silver__wdi_country_year_features') }}

)

select
    s.country_iso3,
    s.year,

    p.population_total,
    p.population_male,
    p.population_female,

    w.gdp_per_capita_current_usd,
    w.gdp_growth_pct,
    w.inflation_cpi_pct,
    w.unemployment_pct,
    w.investment_pct_gdp,

    w.secondary_enrollment_pct,
    w.literacy_rate_pct,
    w.health_expenditure_pct_gdp,
    w.infant_mortality_per_1000,
    w.physicians_per_1000,

    w.gini_income,
    w.poverty_headcount_pct,
    w.urban_population_pct,
    w.youth_unemployment_pct,
    w.dependency_ratio_pct,

    g.vdem_liberal_democracy_index,
    g.vdem_electoral_democracy_index,
    g.vdem_judicial_constraints_index,
    g.vdem_civil_liberties_index

from spine s
left join population p
  on s.country_iso3 = p.country_iso3
 and s.year = p.year
left join wdi_features w
  on s.country_iso3 = w.country_iso3
 and s.year = w.year
left join governance g
  on s.country_iso3 = g.country_iso3
 and s.year = g.year
```

---

## Why This Pattern Works

### 1. Keeps WDI ingestion long and flexible
The bronze/silver ingestion layer remains generic.

### 2. Creates one stable analytical feature table
Analytical models do not need repeated `case when indicator_id = ...` logic.

### 3. Makes domain expansion easy
New indicators only require:
- adding the code in the filter list
- adding one pivot expression
- joining the model into the mart

---

## Recommended Next Implementation Order

### Tonight / Tuesday
Add to `silver__wdi_country_year_features`:

- education
- inequality
- health

### Later
Add separate domain facts or feature models for:

- climate
- conflict
- labor
- technology

---

## Optional dbt Tests

Suggested tests for `silver__wdi_country_year_features`:

```yaml
version: 2

models:
  - name: silver__wdi_country_year_features
    columns:
      - name: country_iso3
        tests:
          - not_null
      - name: year
        tests:
          - not_null
```

If `dbt_utils` is available:

```yaml
      - name: country_iso3
      - name: year
    tests:
      - dbt_utils.unique_combination_of_columns:
          combination_of_columns:
            - country_iso3
            - year
```

---

## Recommended Repository Placement

```text
dbt/models/silver/features/silver__wdi_country_year_features.sql
docs/world2045_dbt_model_pattern.md
```

---

## Practical Outcome

This pattern gives you a clean bridge between:

```text
long-format ingestion
```

and

```text
wide-format analytical modeling
```

which is exactly what the World2045 platform needs for Wednesday's analytics phase.
