{{ config(materialized='table', cluster_by=['country_iso3', 'year']) }}

with base as (

    select
        country_iso3,
        year,
        scenario_id,
        is_forecast_year,
        contribution_gdp_pc,
        contribution_life_expectancy,
        contribution_governance,
        contribution_adaptation_readiness,
        contribution_climate_vulnerability,
        contribution_conflict
    from {{ ref('gold__country_trajectory_score_year_scenario') }}

),

unioned as (

    select country_iso3, year, scenario_id, is_forecast_year, 'gdp_pc' as component, contribution_gdp_pc as contribution_value from base
    union all
    select country_iso3, year, scenario_id, is_forecast_year, 'life_expectancy' as component, contribution_life_expectancy as contribution_value from base
    union all
    select country_iso3, year, scenario_id, is_forecast_year, 'governance' as component, contribution_governance as contribution_value from base
    union all
    select country_iso3, year, scenario_id, is_forecast_year, 'adaptation_readiness' as component, contribution_adaptation_readiness as contribution_value from base
    union all
    select country_iso3, year, scenario_id, is_forecast_year, 'climate_vulnerability' as component, contribution_climate_vulnerability as contribution_value from base
    union all
    select country_iso3, year, scenario_id, is_forecast_year, 'conflict' as component, contribution_conflict as contribution_value from base

)

select *
from unioned