{{ config(materialized='table', cluster_by=['forecast_score_completeness', 'region']) }}

with base as (

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
        is_rankable_forecast_case
    from {{ ref('gold__country_rise_potential') }}

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
        is_rankable_forecast_case,

        0.70 * coalesce(trajectory_change_2023_2045, 0)
      + 0.20 * coalesce(trajectory_score_2045, 0)
      - 0.07 * coalesce(climate_vulnerability_norm_2023, 0)
      - 0.03 * coalesce(conflict_severity_norm_2023, 0) as momentum_score,

        case
            when trajectory_change_2023_2045 >= 0.10 then 'very_high'
            when trajectory_change_2023_2045 >= 0.05 then 'high'
            when trajectory_change_2023_2045 >= 0.02 then 'moderate'
            when trajectory_change_2023_2045 >= -0.01 then 'stable'
            else 'declining'
        end as momentum_band

    from base

)

select *
from final