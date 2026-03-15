{{ config(materialized='table', cluster_by=['quadrant_label', 'region']) }}

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
        momentum_score,
        momentum_band,
        forecast_score_completeness,
        is_rankable_forecast_case
    from {{ ref('gold__country_trajectory_momentum') }}

),

thresholds as (

    select
        approx_quantiles(trajectory_score_2045, 100)[offset(50)] as median_trajectory_score_2045,
        approx_quantiles(momentum_score, 100)[offset(50)] as median_momentum_score
    from base
    where is_rankable_forecast_case = true
      and is_sovereign = true
      and forecast_score_completeness = 'complete'

),

scored as (

    select
        b.*,
        t.median_trajectory_score_2045,
        t.median_momentum_score,

        case
            when b.trajectory_score_2045 >= t.median_trajectory_score_2045 then 'high'
            else 'low'
        end as trajectory_level_2045,

        case
            when b.momentum_score >= t.median_momentum_score then 'high'
            else 'low'
        end as momentum_level

    from base b
    cross join thresholds t

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
        momentum_score,
        momentum_band,

        forecast_score_completeness,
        is_rankable_forecast_case,

        median_trajectory_score_2045,
        median_momentum_score,
        trajectory_level_2045,
        momentum_level,

        case
            when trajectory_level_2045 = 'high' and momentum_level = 'high' then 'Future Leaders'
            when trajectory_level_2045 = 'high' and momentum_level = 'low' then 'Stable Advanced'
            when trajectory_level_2045 = 'low' and momentum_level = 'high' then 'Rising Challengers'
            else 'Structural Risk'
        end as quadrant_label

    from scored

)

select *
from final