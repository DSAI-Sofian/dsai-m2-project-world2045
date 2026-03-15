{{ config(materialized='table', cluster_by=['year']) }}

select
    year,
    scenario_id,
    is_forecast_year,
    avg(trajectory_score) as avg_trajectory_score,
    avg(contribution_gdp_pc) as avg_contribution_gdp_pc,
    avg(contribution_life_expectancy) as avg_contribution_life_expectancy,
    avg(contribution_governance) as avg_contribution_governance,
    avg(contribution_adaptation_readiness) as avg_contribution_adaptation_readiness,
    avg(contribution_climate_vulnerability) as avg_contribution_climate_vulnerability,
    avg(contribution_conflict) as avg_contribution_conflict,
    count(distinct country_iso3) as country_count
from {{ ref('gold__country_trajectory_score_year_scenario') }}
group by 1,2,3