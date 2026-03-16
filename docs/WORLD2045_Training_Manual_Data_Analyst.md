# TRAINING_MANUAL

## Purpose of this manual

This manual is for a new data analyst joining the World2045 project. It explains:

- what the project is trying to answer
- why the warehouse and analytical layers were designed the way they were
- how to validate intermediate and final outputs
- which SQL commands were used to support key findings

This is not a replacement for the dbt models themselves. It is a learning companion that explains the how, what, and why of the platform.

## 1. Project question

The project studies how countries evolve over time and asks:

**Which countries and regions are structurally strongest by 2045, which are improving fastest, and which remain at structural risk?**

To answer this, the project combines historical data with a forecast baseline scenario.

## 2. Why the architecture was designed in layers

### Bronze
Bronze preserves raw source structure so ingestion remains auditable.

### Silver
Silver standardizes country-year facts so different datasets can be aligned.

### Gold
Gold produces wide feature marts and analytical models that are easy to query and visualize.

This separation lets analysts:

- inspect raw data independently
- debug transformation logic by layer
- build analytical models on stable, conformed tables

## 3. Most important tables to understand first

### Historical feature mart
- `gold__mart_world2045_features_country_year`

### Forecast feature mart
- `gold__forecast_feature_country_year`

### Final strategic models
- `gold__country_trajectory_score_year_scenario`
- `gold__country_rise_potential`
- `gold__country_trajectory_momentum`
- `gold__trajectory_country_quadrant`

## 4. Why the trajectory model uses these indicators

The final trajectory score combines six conceptual dimensions:

- income strength: GDP per capita
- population wellbeing: life expectancy
- institutions: governance
- climate resilience: adaptation readiness
- climate exposure: vulnerability penalty
- conflict burden: conflict penalty

The logic is that development is not just wealth. A country can be high-income but still be constrained by weak governance, conflict, or climate vulnerability.

## 5. Why 1995-2023 was chosen for historical scoring

Climate indicators begin in 1995. Because the final score depends on climate variables, the comparable scoring window begins in 1995.

## 6. Why forecast scoring is scenario-based

Only some variables have direct forward projections. GDP and life expectancy projections were available, but governance, climate vulnerability, adaptation readiness, and conflict severity did not have equivalent forecast series in the current stack.

So the project adopted a baseline scenario:

- project GDP per capita and life expectancy directly
- carry forward latest available historical values for missing structural variables

This is analytically honest and auditable.

## 7. SQL validation workflow used in the project

Below are the main SQL commands used to validate the project from feature coverage through final findings. These are grouped by analytical stage.

---

## A. Source and feature coverage validation

### A1. Inspect available country-related tables

Used when deciding which country dimension or conformed-country mapping to use.

```sql
SELECT table_name
FROM `world2045_ci`.INFORMATION_SCHEMA.TABLES
WHERE table_name LIKE '%country%'
ORDER BY table_name;
```

### A2. Inspect feature mart columns

Used to identify exact field names before writing the scenario model.

```sql
select
  table_name,
  column_name,
  data_type
from `world2045_ci`.INFORMATION_SCHEMA.COLUMNS
where table_name in (
  'gold__features_world2045_normalized_country_year',
  'gold__mart_world2045_features_analytic_1960_2023',
  'gold__mart_world2045_features_country_year'
)
order by table_name, ordinal_position;
```

### A3. Inspect country mapping columns

Used to find the correct regional metadata fields.

```sql
select
  table_name,
  column_name,
  data_type
from `world2045_ci`.INFORMATION_SCHEMA.COLUMNS
where table_name in (
  'dim__country',
  'country_overrides'
)
order by table_name, ordinal_position;
```

### A4. Preview feature marts

Used to validate that candidate marts actually contain the needed fields.

```sql
select *
from `world2045_ci.gold__mart_world2045_features_country_year`
limit 5;
```

```sql
select *
from `world2045_ci.gold__mart_world2045_features_analytic_1960_2023`
limit 5;
```

```sql
select *
from `world2045_ci.gold__features_world2045_normalized_country_year`
limit 5;
```

---

## B. Forecast feature validation

### B1. Check forecast years and row coverage

Used after building forecast tables.

```sql
select
  min(year) as min_year,
  max(year) as max_year,
  count(*) as row_count,
  count(distinct country_iso3) as country_count
from `world2045_ci.gold__forecast_feature_country_year`;
```

### B2. Null coverage for core forecast fields

```sql
select
  count(*) as rows_total,
  countif(fertility_rate is null) as fertility_nulls,
  countif(life_expectancy_birth_both is null) as life_expectancy_nulls,
  countif(net_migrants_thousands is null) as migration_nulls
from `world2045_ci.gold__forecast_feature_country_year`;
```

---

## C. Historical trajectory validation

### C1. Scenario / score coverage check

```sql
select
  scenario_id,
  min(year) as min_year,
  max(year) as max_year,
  count(*) as row_count,
  count(distinct country_iso3) as country_count
from `world2045_ci.gold__country_trajectory_score_year_scenario`
group by 1
order by 1;
```

### C2. Forecast null leakage check

```sql
select
  count(*) as total_rows,
  countif(trajectory_score is null) as null_trajectory_score_rows,
  countif(gdp_pc_norm is null) as null_gdp_norm_rows,
  countif(life_expectancy_norm is null) as null_life_expectancy_norm_rows,
  countif(governance_norm is null) as null_governance_norm_rows,
  countif(adaptation_readiness_norm is null) as null_adaptation_norm_rows,
  countif(climate_vulnerability_norm is null) as null_climate_norm_rows,
  countif(conflict_severity_norm is null) as null_conflict_norm_rows
from `world2045_ci.gold__country_trajectory_score_year_scenario`
where is_forecast_year = true;
```

### C3. 2023 vs 2045 country comparison

Used to inspect major movers.

```sql
with base as (
  select
    country_iso3,
    year,
    trajectory_score
  from `world2045_ci.gold__country_trajectory_score_year_scenario`
  where scenario_id in ('historical_observed', 'baseline_static_risk')
    and year in (2023, 2045)
),
pivoted as (
  select
    country_iso3,
    max(case when year = 2023 then trajectory_score end) as score_2023,
    max(case when year = 2045 then trajectory_score end) as score_2045
  from base
  group by 1
)
select
  country_iso3,
  score_2023,
  score_2045,
  score_2045 - score_2023 as score_change_2023_2045
from pivoted
order by score_change_2023_2045 desc
limit 50;
```

---

## D. Forecast completeness validation

### D1. Forecast completeness counts

Used to determine how many forecast cases were complete vs partial.

```sql
select
  case
    when vdem_liberal_democracy_index is not null
     and adaptation_readiness is not null
     and climate_vulnerability is not null
     and conflict_severity is not null
    then 'complete'
    else 'partial'
  end as forecast_score_completeness,
  count(distinct country_iso3) as country_count
from `world2045_ci.gold__country_trajectory_score_year_scenario`
where is_forecast_year = true
group by 1
order by 1;
```

### D2. Coverage diagnosis for partial rows

Used to identify which countries had missing carried-forward components.

```sql
select
  country_iso3,
  count(*) as forecast_rows,
  max(case when vdem_liberal_democracy_index is null then 1 else 0 end) as governance_missing,
  max(case when adaptation_readiness is null then 1 else 0 end) as adaptation_missing,
  max(case when climate_vulnerability is null then 1 else 0 end) as climate_missing,
  max(case when conflict_severity is null then 1 else 0 end) as conflict_missing
from `world2045_ci.gold__country_trajectory_score_year_scenario`
where is_forecast_year = true
  and (
    vdem_liberal_democracy_index is null
    or adaptation_readiness is null
    or climate_vulnerability is null
    or conflict_severity is null
  )
group by 1
order by forecast_rows desc, country_iso3;
```

### D3. ISO mapping gaps for regional analysis

Used to identify unmatched forecast ISO3 values.

```sql
select
  s.country_iso3
from `world2045_ci.gold__country_trajectory_score_year_scenario` s
left join `world2045_ci.country_overrides` d
  on s.country_iso3 = d.iso3
where s.year = 2045
  and s.scenario_id = 'baseline_static_risk'
  and d.iso3 is null
group by 1
order by 1;
```

---

## E. Region and subregion validation

### E1. Region-level spot check

Used to inspect a few anchor years.

```sql
select
  region,
  year,
  scenario_id,
  avg_trajectory_score,
  country_count
from `world2045_ci.gold__region_trajectory_score_year`
where year in (1995, 2023, 2045)
order by region, year;
```

### E2. Top subregions by 2045 score

Used to support regional findings.

```sql
select
  region,
  subregion,
  avg_trajectory_score,
  country_count
from `world2045_ci.gold__subregion_trajectory_score_year`
where year = 2045
  and scenario_id = 'baseline_static_risk'
order by avg_trajectory_score desc
limit 25;
```

---

## F. Rise potential validation

### F1. Coverage by completeness

```sql
select
  forecast_score_completeness,
  count(*) as row_count,
  countif(is_rankable_forecast_case) as rankable_count
from `world2045_ci.gold__country_rise_potential`
group by 1
order by 1;
```

### F2. Top 25 rise-potential countries

```sql
select
  country_iso3,
  country_name,
  region,
  subregion,
  trajectory_score_2023,
  trajectory_score_2045,
  trajectory_change_2023_2045,
  rise_potential_score
from `world2045_ci.gold__country_rise_potential`
where is_rankable_forecast_case = true
  and is_sovereign = true
order by rise_potential_score desc
limit 25;
```

### F3. Top 10 by region

```sql
with ranked as (
  select
    *,
    row_number() over (
      partition by region
      order by rise_potential_score desc
    ) as rn
  from `world2045_ci.gold__country_rise_potential`
  where is_rankable_forecast_case = true
    and is_sovereign = true
    and region is not null
)
select
  region,
  country_iso3,
  country_name,
  rise_potential_score,
  trajectory_change_2023_2045
from ranked
where rn <= 10
order by region, rn;
```

---

## G. Momentum validation

### G1. Top 25 momentum countries

```sql
select
  country_iso3,
  country_name,
  region,
  subregion,
  trajectory_score_2023,
  trajectory_score_2045,
  trajectory_change_2023_2045,
  momentum_score,
  momentum_band
from `world2045_ci.gold__country_trajectory_momentum`
where is_rankable_forecast_case = true
  and is_sovereign = true
order by momentum_score desc
limit 25;
```

### G2. Top 10 momentum countries by region

```sql
with ranked as (
  select
    *,
    row_number() over (
      partition by region
      order by momentum_score desc
    ) as rn
  from `world2045_ci.gold__country_trajectory_momentum`
  where is_rankable_forecast_case = true
    and is_sovereign = true
    and region is not null
)
select
  region,
  country_iso3,
  country_name,
  momentum_score,
  trajectory_change_2023_2045,
  momentum_band
from ranked
where rn <= 10
order by region, rn;
```

### G3. Distribution by momentum band

```sql
select
  momentum_band,
  count(*) as country_count
from `world2045_ci.gold__country_trajectory_momentum`
where is_rankable_forecast_case = true
  and is_sovereign = true
group by 1
order by
  case momentum_band
    when 'very_high' then 1
    when 'high' then 2
    when 'moderate' then 3
    when 'low_positive' then 4
    when 'negative' then 5
    else 6
  end;
```

---

## H. Quadrant validation

### H1. Quadrant distribution

```sql
select
  quadrant_label,
  count(*) as country_count
from `world2045_ci.gold__trajectory_country_quadrant`
where is_rankable_forecast_case = true
  and is_sovereign = true
group by 1
order by country_count desc;
```

### H2. Top countries in each quadrant

```sql
with ranked as (
  select
    *,
    row_number() over (
      partition by quadrant_label
      order by momentum_score desc, trajectory_score_2045 desc
    ) as rn
  from `world2045_ci.gold__trajectory_country_quadrant`
  where is_rankable_forecast_case = true
    and is_sovereign = true
)
select
  quadrant_label,
  country_iso3,
  country_name,
  region,
  trajectory_score_2045,
  momentum_score,
  trajectory_change_2023_2045
from ranked
where rn <= 10
order by quadrant_label, rn;
```

### H3. Regional quadrant mix

```sql
select
  region,
  quadrant_label,
  count(*) as country_count
from `world2045_ci.gold__trajectory_country_quadrant`
where is_rankable_forecast_case = true
  and is_sovereign = true
group by 1,2
order by region, quadrant_label;
```

## 8. How the main findings were reasoned

### Example: "Guyana is the standout upward mover"
Reasoning path:

1. run top 25 rise-potential query
2. run top 25 momentum query
3. confirm Guyana appears at the top of both or near top of both
4. inspect `trajectory_change_2023_2045`

### Example: "Europe dominates upper-tier projected outcomes"
Reasoning path:

1. run top subregion 2045 query
2. run region spot check
3. run quadrant regional mix query
4. compare Europe against Africa, Americas, and Asia

### Example: "Africa remains concentrated in structural risk"
Reasoning path:

1. run regional quadrant mix query
2. confirm Africa has the largest count in `Structural Risk`
3. compare challenger count and future-leader count

## 9. Final learning guidance

When validating a model, always ask:

1. Does the row coverage look correct?
2. Does the year range look correct?
3. Are nulls concentrated in specific countries or whole regions?
4. Do rankings make structural sense?
5. Are country classifications driven by level, momentum, or both?

This project is strongest when interpreted as a transparent, layered analytical system rather than as a black-box forecast engine.
