{{ config(materialized='table', cluster_by=['forecast_score_completeness', 'region']) }}

with score_2023 as (

    select
        country_iso3,
        trajectory_score as trajectory_score_2023,
        climate_vulnerability_norm as climate_vulnerability_norm_2023,
        conflict_severity_norm as conflict_severity_norm_2023
    from {{ ref('gold__country_trajectory_score_year_scenario') }}
    where year = 2023
      and scenario_id = 'historical_observed'

),

score_2045 as (

    select
        country_iso3,
        trajectory_score as trajectory_score_2045,
        forecast_score_completeness
    from {{ ref('gold__country_trajectory_score_year_scenario') }}
    where year = 2045
      and scenario_id = 'baseline_static_risk'

),

country_dim as (

    select
        iso3 as country_iso3,
        country_name,
        region,
        subregion,
        income_group,
        is_sovereign
    from {{ ref('country_overrides') }}

),

combined as (

    select
        d.country_name,
        d.region,
        d.subregion,
        d.income_group,
        d.is_sovereign,

        s23.country_iso3,
        s23.trajectory_score_2023,
        s45.trajectory_score_2045,
        s45.forecast_score_completeness,
        s23.climate_vulnerability_norm_2023,
        s23.conflict_severity_norm_2023,

        s45.trajectory_score_2045 - s23.trajectory_score_2023 as trajectory_change_2023_2045

    from score_2023 s23
    inner join score_2045 s45
      on s23.country_iso3 = s45.country_iso3
    left join country_dim d
      on s23.country_iso3 = d.country_iso3

),

final as (

    select
        country_iso3,
        country_name,
        region,
        subregion,
        income_group,
        is_sovereign,

        trajectory_score_2023,
        trajectory_score_2045,
        trajectory_change_2023_2045,
        climate_vulnerability_norm_2023,
        conflict_severity_norm_2023,
        forecast_score_completeness,

        0.50 * coalesce(trajectory_change_2023_2045, 0)
      + 0.35 * coalesce(trajectory_score_2045, 0)
      - 0.10 * coalesce(climate_vulnerability_norm_2023, 0)
      - 0.05 * coalesce(conflict_severity_norm_2023, 0) as rise_potential_score,

        case
            when forecast_score_completeness = 'complete' then true
            else false
        end as is_rankable_forecast_case

    from combined

)

select *
from final