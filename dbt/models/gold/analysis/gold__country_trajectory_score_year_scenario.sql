{{ config(materialized='table') }}

with historical_features as (

    select
        country_iso3,
        year,
        gdp_per_capita_current_usd,
        life_expectancy_years,
        vdem_liberal_democracy_index,
        adaptation_readiness,
        climate_vulnerability,
        battle_deaths
    from {{ ref('gold__mart_world2045_features_country_year') }}
    where year between 1995 and 2023
      and gdp_per_capita_current_usd is not null
      and life_expectancy_years is not null
      and vdem_liberal_democracy_index is not null
      and adaptation_readiness is not null
      and climate_vulnerability is not null

),

forecast_features as (

    select
        country_iso3,
        year,
        gdp_real_per_capita_usd as gdp_per_capita_current_usd,
        life_expectancy_birth_both as life_expectancy_years
    from {{ ref('gold__forecast_feature_country_year') }}
    where year between 2024 and 2045

),

historical_conflict as (

    select
        country_iso3,
        year,
        ln(1 + coalesce(battle_deaths, 0)) as conflict_severity
    from historical_features

),

historical_base as (

    select
        h.country_iso3,
        h.year,
        'historical_observed' as scenario_id,
        false as is_forecast_year,

        h.gdp_per_capita_current_usd,
        h.life_expectancy_years,
        h.vdem_liberal_democracy_index,
        h.adaptation_readiness,
        h.climate_vulnerability,
        hc.conflict_severity,

        'observed_historical' as climate_vulnerability_projection_source,
        'observed_historical' as climate_vulnerability_forecast_method
    from historical_features h
    left join historical_conflict hc
      on h.country_iso3 = hc.country_iso3
     and h.year = hc.year

),

latest_observed_state as (

    select
        country_iso3,
        array_agg(vdem_liberal_democracy_index ignore nulls order by year desc limit 1)[safe_offset(0)] as vdem_liberal_democracy_index,
        array_agg(adaptation_readiness ignore nulls order by year desc limit 1)[safe_offset(0)] as adaptation_readiness,
        array_agg(climate_vulnerability ignore nulls order by year desc limit 1)[safe_offset(0)] as climate_vulnerability,
        array_agg(conflict_severity ignore nulls order by year desc limit 1)[safe_offset(0)] as conflict_severity
    from historical_base
    where year <= 2023
    group by country_iso3

),

ml_climate_projection as (

    select
        country_iso3,
        year,
        projected_value as climate_vulnerability_ml,
        projection_source as climate_vulnerability_projection_source,
        forecast_method as climate_vulnerability_forecast_method
    from {{ ref('silver__projection_structural_risk_country_year') }}
    where scenario_id = 'baseline_ml_dynamic_risk'
      and indicator_name = 'climate_vulnerability'
      and year between 2024 and 2045

),

forecast_base_static as (

    select
        f.country_iso3,
        f.year,
        'baseline_static_risk' as scenario_id,
        true as is_forecast_year,

        f.gdp_per_capita_current_usd,
        f.life_expectancy_years,
        los.vdem_liberal_democracy_index,
        los.adaptation_readiness,
        los.climate_vulnerability,
        los.conflict_severity,

        'carry_forward_latest_observed' as climate_vulnerability_projection_source,
        'carry_forward_baseline' as climate_vulnerability_forecast_method
    from forecast_features f
    left join latest_observed_state los
      on f.country_iso3 = los.country_iso3

),

forecast_base_ml as (

    select
        f.country_iso3,
        f.year,
        'baseline_ml_dynamic_risk' as scenario_id,
        true as is_forecast_year,

        f.gdp_per_capita_current_usd,
        f.life_expectancy_years,
        los.vdem_liberal_democracy_index,
        los.adaptation_readiness,
        coalesce(ml.climate_vulnerability_ml, los.climate_vulnerability) as climate_vulnerability,
        los.conflict_severity,

        coalesce(ml.climate_vulnerability_projection_source, 'carry_forward_latest_observed') as climate_vulnerability_projection_source,
        coalesce(ml.climate_vulnerability_forecast_method, 'carry_forward_baseline') as climate_vulnerability_forecast_method
    from forecast_features f
    left join latest_observed_state los
      on f.country_iso3 = los.country_iso3
    left join ml_climate_projection ml
      on f.country_iso3 = ml.country_iso3
     and f.year = ml.year

),

combined as (

    select * from historical_base
    union all
    select * from forecast_base_static
    union all
    select * from forecast_base_ml

),

year_bounds as (

    select
        scenario_id,
        year,

        min(gdp_per_capita_current_usd) as min_gdp_per_capita_current_usd,
        max(gdp_per_capita_current_usd) as max_gdp_per_capita_current_usd,

        min(life_expectancy_years) as min_life_expectancy_years,
        max(life_expectancy_years) as max_life_expectancy_years,

        min(vdem_liberal_democracy_index) as min_vdem_liberal_democracy_index,
        max(vdem_liberal_democracy_index) as max_vdem_liberal_democracy_index,

        min(adaptation_readiness) as min_adaptation_readiness,
        max(adaptation_readiness) as max_adaptation_readiness,

        min(climate_vulnerability) as min_climate_vulnerability,
        max(climate_vulnerability) as max_climate_vulnerability,

        min(conflict_severity) as min_conflict_severity,
        max(conflict_severity) as max_conflict_severity
    from combined
    group by scenario_id, year

),

normalized as (

    select
        c.country_iso3,
        c.year,
        c.scenario_id,
        c.is_forecast_year,

        c.gdp_per_capita_current_usd,
        c.life_expectancy_years,
        c.vdem_liberal_democracy_index,
        c.adaptation_readiness,
        c.climate_vulnerability,
        c.conflict_severity,
        c.climate_vulnerability_projection_source,
        c.climate_vulnerability_forecast_method,

        case
            when yb.max_gdp_per_capita_current_usd = yb.min_gdp_per_capita_current_usd then null
            else (c.gdp_per_capita_current_usd - yb.min_gdp_per_capita_current_usd)
                / nullif(yb.max_gdp_per_capita_current_usd - yb.min_gdp_per_capita_current_usd, 0)
        end as gdp_pc_norm,

        case
            when yb.max_life_expectancy_years = yb.min_life_expectancy_years then null
            else (c.life_expectancy_years - yb.min_life_expectancy_years)
                / nullif(yb.max_life_expectancy_years - yb.min_life_expectancy_years, 0)
        end as life_expectancy_norm,

        case
            when yb.max_vdem_liberal_democracy_index = yb.min_vdem_liberal_democracy_index then null
            else (c.vdem_liberal_democracy_index - yb.min_vdem_liberal_democracy_index)
                / nullif(yb.max_vdem_liberal_democracy_index - yb.min_vdem_liberal_democracy_index, 0)
        end as governance_norm,

        case
            when yb.max_adaptation_readiness = yb.min_adaptation_readiness then null
            else (c.adaptation_readiness - yb.min_adaptation_readiness)
                / nullif(yb.max_adaptation_readiness - yb.min_adaptation_readiness, 0)
        end as adaptation_readiness_norm,

        case
            when yb.max_climate_vulnerability = yb.min_climate_vulnerability then null
            else (c.climate_vulnerability - yb.min_climate_vulnerability)
                / nullif(yb.max_climate_vulnerability - yb.min_climate_vulnerability, 0)
        end as climate_vulnerability_norm,

        case
            when yb.max_conflict_severity = yb.min_conflict_severity then null
            else (c.conflict_severity - yb.min_conflict_severity)
                / nullif(yb.max_conflict_severity - yb.min_conflict_severity, 0)
        end as conflict_severity_norm
    from combined c
    left join year_bounds yb
      on c.year = yb.year
     and c.scenario_id = yb.scenario_id

),

scored as (

    select
        country_iso3,
        year,
        scenario_id,
        is_forecast_year,

        gdp_per_capita_current_usd,
        life_expectancy_years,
        vdem_liberal_democracy_index,
        adaptation_readiness,
        climate_vulnerability,
        conflict_severity,
        climate_vulnerability_projection_source,
        climate_vulnerability_forecast_method,

        gdp_pc_norm,
        life_expectancy_norm,
        governance_norm,
        adaptation_readiness_norm,
        climate_vulnerability_norm,
        conflict_severity_norm,

        0.30 * coalesce(gdp_pc_norm, 0)
      + 0.25 * coalesce(life_expectancy_norm, 0)
      + 0.20 * coalesce(governance_norm, 0)
      + 0.15 * coalesce(adaptation_readiness_norm, 0)
      - 0.10 * coalesce(climate_vulnerability_norm, 0)
      - 0.10 * coalesce(conflict_severity_norm, 0) as trajectory_score,

        0.30 * coalesce(gdp_pc_norm, 0) as contribution_gdp_pc,
        0.25 * coalesce(life_expectancy_norm, 0) as contribution_life_expectancy,
        0.20 * coalesce(governance_norm, 0) as contribution_governance,
        0.15 * coalesce(adaptation_readiness_norm, 0) as contribution_adaptation_readiness,
       -0.10 * coalesce(climate_vulnerability_norm, 0) as contribution_climate_vulnerability,
       -0.10 * coalesce(conflict_severity_norm, 0) as contribution_conflict,

        case
            when scenario_id = 'baseline_static_risk' then 'Forward score uses projected GDP per capita and life expectancy, with governance, climate vulnerability, adaptation readiness, and conflict risk carried forward from the latest observed year.'
            when scenario_id = 'baseline_ml_dynamic_risk' then 'Forward score uses projected GDP per capita and life expectancy, with climate vulnerability from ML projection (fallback to carry-forward), while governance, adaptation readiness, and conflict risk remain carry-forward from the latest observed year.'
            else 'Observed-year score based on historical indicator values.'
        end as assumption_flag,

        case
            when vdem_liberal_democracy_index is not null
            and adaptation_readiness is not null
            and climate_vulnerability is not null
            and conflict_severity is not null
            then 'complete'
            else 'partial'
        end as forecast_score_completeness
    from normalized

)

select *
from scored
