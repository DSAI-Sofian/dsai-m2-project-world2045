{{ config(materialized='table') }}

with base as (

    select
        p.country_iso3,
        p.year,

        -- demographic / forecast features
        p.population_total,
        p.fertility_rate,
        p.life_expectancy_birth_both,
        p.net_migrants_thousands,

        -- projected GDP if available in forecast layer
        p.gdp_real_billion_usd,

        -- climate / resilience
        ng.nd_gain_score,
        ng.nd_gain_readiness,
        ng.nd_gain_vulnerability,

        -- governance
        gv.governance_score,

        -- conflict / stability
        cf.battle_deaths,
        cf.conflict_intensity
    from {{ ref('gold__forecast_feature_country_year') }} p
    left join {{ ref('silver__nd_gain_country_year') }} ng
      on p.country_iso3 = ng.country_iso3
     and p.year = ng.year
    left join {{ ref('silver__governance_country_year') }} gv
      on p.country_iso3 = gv.country_iso3
     and p.year = gv.year
    left join {{ ref('silver__conflict_country_year') }} cf
      on p.country_iso3 = cf.country_iso3
     and p.year = cf.year
    where p.year between 2025 and 2045

),

scored as (

    select
        country_iso3,
        year,

        population_total,
        fertility_rate,
        life_expectancy_birth_both,
        net_migrants_thousands,
        gdp_real_billion_usd,
        nd_gain_score,
        nd_gain_readiness,
        nd_gain_vulnerability,
        governance_score,
        battle_deaths,
        conflict_intensity,

        -- economic: relative GDP position
        percent_rank() over (
            partition by year
            order by gdp_real_billion_usd
        ) as economic_score,

        -- demographic: high life expectancy + moderate fertility is directionally favorable
        (
            0.7 * percent_rank() over (
                partition by year
                order by life_expectancy_birth_both
            )
            +
            0.3 * (
                1 - percent_rank() over (
                    partition by year
                    order by fertility_rate
                )
            )
        ) as demographic_score,

        -- resilience: higher readiness / lower vulnerability is better
        (
            0.5 * percent_rank() over (
                partition by year
                order by nd_gain_readiness
            )
            +
            0.5 * (
                1 - percent_rank() over (
                    partition by year
                    order by nd_gain_vulnerability
                )
            )
        ) as resilience_score,

        -- stability: lower conflict is better, higher governance is better
        (
            0.6 * percent_rank() over (
                partition by year
                order by governance_score
            )
            +
            0.4 * (
                1 - percent_rank() over (
                    partition by year
                    order by coalesce(battle_deaths, 0)
                )
            )
        ) as stability_score

    from base

),

final as (

    select
        country_iso3,
        year,

        economic_score,
        demographic_score,
        resilience_score,
        stability_score,

        (
            0.30 * economic_score +
            0.25 * demographic_score +
            0.20 * resilience_score +
            0.25 * stability_score
        ) as trajectory_score,

        (
            (
                0.30 * economic_score +
                0.25 * demographic_score +
                0.20 * resilience_score +
                0.25 * stability_score
            )
            -
            lag(
                0.30 * economic_score +
                0.25 * demographic_score +
                0.20 * resilience_score +
                0.25 * stability_score
            , 5) over (
                partition by country_iso3
                order by year
            )
        ) as trajectory_score_5y_delta

    from scored

)

select
    country_iso3,
    year,
    economic_score,
    demographic_score,
    resilience_score,
    stability_score,
    trajectory_score,
    trajectory_score_5y_delta,
    case
        when trajectory_score >= 0.80 then 'very_high'
        when trajectory_score >= 0.60 then 'high'
        when trajectory_score >= 0.40 then 'medium'
        when trajectory_score >= 0.20 then 'low'
        else 'very_low'
    end as trajectory_band
from final