{{ config(materialized='table', cluster_by=['region', 'subregion', 'year']) }}

select
    d.region,
    d.subregion,
    s.year,
    s.scenario_id,
    s.is_forecast_year,
    avg(s.trajectory_score) as avg_trajectory_score,
    avg(s.contribution_gdp_pc) as avg_contribution_gdp_pc,
    avg(s.contribution_life_expectancy) as avg_contribution_life_expectancy,
    avg(s.contribution_governance) as avg_contribution_governance,
    avg(s.contribution_adaptation_readiness) as avg_contribution_adaptation_readiness,
    avg(s.contribution_climate_vulnerability) as avg_contribution_climate_vulnerability,
    avg(s.contribution_conflict) as avg_contribution_conflict,
    count(distinct s.country_iso3) as country_count
from {{ ref('gold__country_trajectory_score_year_scenario') }} s
left join {{ ref('country_overrides') }} d
  on s.country_iso3 = d.iso3
where d.region is not null
  and d.subregion is not null
  and d.is_sovereign = true
group by
    d.region,
    d.subregion,
    s.year,
    s.scenario_id,
    s.is_forecast_year