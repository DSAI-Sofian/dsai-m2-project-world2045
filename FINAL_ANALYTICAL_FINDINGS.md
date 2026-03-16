# FINAL ANALYTICAL FINDINGS

## Purpose of this document

This document summarizes the final analytical findings of the World2045 project and pairs each major conclusion with the validation SQL used to support it. The goal is traceability: a reviewer should be able to see not only the claim, but also the exact query pattern used to generate the evidence.

## 1. Forecast coverage and interpretation

### Finding
The forecast scenario covers 2024-2045, but not all countries have complete carried-forward structural variables. The final validated split was:

- complete forecast countries: 154
- partial forecast countries: 83

This means forecast rankings are strongest when filtered to complete cases.

### Validation SQL - Forecast completeness summary

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

## 2. Baseline forward trajectory remains structurally unequal

### Finding
The 2045 baseline scenario remains strongly stratified. Western Europe, Northern Europe, Australia and New Zealand, Northern America, and Eastern Asia remain among the strongest projected subregions.

### Validation SQL - Top 2045 subregions by projected average trajectory

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

## 3. Region-level structure persists into 2045

### Finding
Europe remains the strongest overall regional bloc. Africa remains the most structurally constrained region under the baseline scenario. Asia is the most heterogeneous.

### Validation SQL - Region-level comparison at anchor years

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

## 4. Guyana is the strongest upward-movement outlier

### Finding
Guyana emerged as the clearest high-momentum and high-rise-potential outlier by 2045.

### Validation SQL - Top 25 rise-potential countries

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

### Validation SQL - Top 25 momentum countries

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

## 5. Rise potential and momentum are not the same thing

### Finding
The project distinguished between:

- **rise potential**: strategic 2045 positioning plus change
- **momentum**: improvement pace

This matters because many advanced countries rank highly in rise potential even when their relative change is slightly negative.

### Validation SQL - Top 10 by region for rise potential

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

### Validation SQL - Top 10 by region for momentum

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

## 6. Momentum is concentrated in a small number of countries

### Finding
The momentum distribution is highly skewed. Only a very small number of countries exhibit strong positive momentum under the baseline scenario.

Validated distribution:

- very_high: 1
- moderate: 4
- low_positive: 67
- negative: 78

### Validation SQL - Momentum band distribution

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

## 7. Europe dominates high-trajectory country positioning

### Finding
Europe contributes a very large share of upper-tier country outcomes and is strongly concentrated in the upper quadrants.

### Validation SQL - Regional quadrant mix

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

## 8. Africa remains concentrated in structural risk

### Finding
Africa has the largest number of countries in the `Structural Risk` quadrant and comparatively few in `Future Leaders`.

### Validation SQL - Regional quadrant mix

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

## 9. Asia is the most heterogeneous major region

### Finding
Asia spans all four strategic categories and displays the widest internal variation among major regions.

### Validation SQL - Regional quadrant mix

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

## 10. Final quadrant segmentation gives the cleanest strategic summary

### Finding
The final median-threshold quadrant distribution was:

- Future Leaders: 68
- Structural Risk: 66
- Rising Challengers: 8
- Stable Advanced: 8

This is a strong final strategic summary because it combines both projected 2045 level and development momentum.

### Validation SQL - Final quadrant distribution

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

### Validation SQL - Top countries in each quadrant

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

## 11. Final interpretation

The completed World2045 platform indicates that long-run development hierarchy remains relatively persistent under a baseline continuation scenario. Europe and selected advanced Asia-Pacific states continue to dominate upper-tier outcomes, Africa remains concentrated in structural-risk conditions, and only a small number of countries emerge as true upward challengers. The project therefore supports a nuanced conclusion: **there is movement, but global convergence remains limited and uneven through 2045**.

## 12. Important methodological caution

The analytical findings are strongest when interpreted with three caveats:

1. forward structural variables are carried forward, not fully projected
2. some countries have partial forecast component coverage
3. all score changes are relative to per-year normalization, so slight negative relative movement does not imply absolute decline

## Acknowledgements

Portions of the technical design, debugging support, and documentation refinement for this project were assisted by **ChatGPT (OpenAI)**. All final implementation decisions, data engineering work, analytical modeling, and system integration were performed by the project author.
