{{ config(
    materialized='table'
) }}

with base as (

    select
        country_iso3,
        year,

        gdp_per_capita_current_usd,
        life_expectancy_years,
        vdem_liberal_democracy_index,
        gini_index,
        climate_vulnerability,
        adaptation_readiness,

        coalesce(battle_deaths, 0) as battle_deaths,
        coalesce(conflict_incidence, 0) as conflict_incidence,
        coalesce(war_intensity, 0) as war_intensity

    from {{ ref('gold__mart_world2045_features_country_year') }}
    where year between 1995 and 2045
),

features as (

    select
        country_iso3,
        year,

        gdp_per_capita_current_usd,
        life_expectancy_years,
        vdem_liberal_democracy_index,
        gini_index,
        climate_vulnerability,
        adaptation_readiness,
        battle_deaths,
        conflict_incidence,
        war_intensity,

        ln(1 + battle_deaths) as conflict_severity_raw,

        case
            when gdp_per_capita_current_usd is not null
             and life_expectancy_years is not null
             and vdem_liberal_democracy_index is not null
             and climate_vulnerability is not null
             and adaptation_readiness is not null
            then 1 else 0
        end as score_core_ready

    from base
),

year_stats as (

    select
        year,

        min(gdp_per_capita_current_usd) as min_gdp_pc,
        max(gdp_per_capita_current_usd) as max_gdp_pc,

        min(life_expectancy_years) as min_life_exp,
        max(life_expectancy_years) as max_life_exp,

        min(vdem_liberal_democracy_index) as min_governance,
        max(vdem_liberal_democracy_index) as max_governance,

        min(gini_index) as min_gini,
        max(gini_index) as max_gini,

        min(climate_vulnerability) as min_climate_vulnerability,
        max(climate_vulnerability) as max_climate_vulnerability,

        min(adaptation_readiness) as min_adaptation_readiness,
        max(adaptation_readiness) as max_adaptation_readiness,

        min(conflict_severity_raw) as min_conflict_severity,
        max(conflict_severity_raw) as max_conflict_severity

    from features
    where score_core_ready = 1
    group by year
),

normalized as (

    select
        f.country_iso3,
        f.year,

        f.gdp_per_capita_current_usd,
        f.life_expectancy_years,
        f.vdem_liberal_democracy_index,
        f.gini_index,
        f.climate_vulnerability,
        f.adaptation_readiness,
        f.battle_deaths,
        f.conflict_incidence,
        f.war_intensity,
        f.conflict_severity_raw,
        f.score_core_ready,

        case
            when f.score_core_ready = 1 and s.max_gdp_pc > s.min_gdp_pc
            then (f.gdp_per_capita_current_usd - s.min_gdp_pc) / (s.max_gdp_pc - s.min_gdp_pc)
        end as gdp_pc_norm,

        case
            when f.score_core_ready = 1 and s.max_life_exp > s.min_life_exp
            then (f.life_expectancy_years - s.min_life_exp) / (s.max_life_exp - s.min_life_exp)
        end as life_expectancy_norm,

        case
            when f.score_core_ready = 1 and s.max_governance > s.min_governance
            then (f.vdem_liberal_democracy_index - s.min_governance) / (s.max_governance - s.min_governance)
        end as governance_norm,

        case
            when f.score_core_ready = 1 and s.max_gini > s.min_gini
            then (f.gini_index - s.min_gini) / (s.max_gini - s.min_gini)
        end as inequality_norm,

        case
            when f.score_core_ready = 1 and s.max_climate_vulnerability > s.min_climate_vulnerability
            then (f.climate_vulnerability - s.min_climate_vulnerability) / (s.max_climate_vulnerability - s.min_climate_vulnerability)
        end as climate_vulnerability_norm,

        case
            when f.score_core_ready = 1 and s.max_adaptation_readiness > s.min_adaptation_readiness
            then (f.adaptation_readiness - s.min_adaptation_readiness) / (s.max_adaptation_readiness - s.min_adaptation_readiness)
        end as adaptation_readiness_norm,

        case
            when f.score_core_ready = 1 and s.max_conflict_severity > s.min_conflict_severity
            then (f.conflict_severity_raw - s.min_conflict_severity) / (s.max_conflict_severity - s.min_conflict_severity)
            when f.score_core_ready = 1
            then 0
        end as conflict_severity_norm

    from features f
    left join year_stats s
        on f.year = s.year
),

scored as (

    select
        *,
        case
            when score_core_ready = 1 then
                  0.28 * gdp_pc_norm
                + 0.24 * life_expectancy_norm
                + 0.18 * governance_norm
                + 0.14 * adaptation_readiness_norm
                - 0.10 * climate_vulnerability_norm
                - 0.06 * conflict_severity_norm
        end as trajectory_score
    from normalized
),

ranked as (

    select
        *,
        case
            when trajectory_score is not null then
                rank() over (
                    partition by year
                    order by trajectory_score desc, country_iso3
                )
        end as trajectory_rank
    from scored
)

select
    country_iso3,
    year,

    gdp_per_capita_current_usd,
    life_expectancy_years,
    vdem_liberal_democracy_index,
    gini_index,
    climate_vulnerability,
    adaptation_readiness,
    battle_deaths,
    conflict_incidence,
    war_intensity,
    conflict_severity_raw,

    gdp_pc_norm,
    life_expectancy_norm,
    governance_norm,
    inequality_norm,
    climate_vulnerability_norm,
    adaptation_readiness_norm,
    conflict_severity_norm,

    score_core_ready,
    trajectory_score,
    trajectory_rank,

    case
        when trajectory_score is null then null
        when trajectory_score >= 0.70 then 'Tier 1'
        when trajectory_score >= 0.55 then 'Tier 2'
        when trajectory_score >= 0.40 then 'Tier 3'
        else 'Tier 4'
    end as trajectory_band,

    'v1_weighted_composite' as score_version

from ranked