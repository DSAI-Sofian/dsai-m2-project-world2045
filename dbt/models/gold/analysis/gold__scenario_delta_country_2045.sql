{{ config(materialized='table', cluster_by=['region']) }}

with static_2045 as (

    select
        country_iso3,
        trajectory_score as trajectory_score_static_2045,
        rank() over (
            order by trajectory_score desc, country_iso3
        ) as trajectory_rank_static_2045,
        forecast_score_completeness as forecast_score_completeness_static
    from {{ ref('gold__country_trajectory_score_year_scenario') }}
    where year = 2045
      and scenario_id = 'baseline_static_risk'

),

ml_2045 as (

    select
        country_iso3,
        trajectory_score as trajectory_score_ml_2045,
        rank() over (
            order by trajectory_score desc, country_iso3
        ) as trajectory_rank_ml_2045,
        forecast_score_completeness as forecast_score_completeness_ml
    from {{ ref('gold__country_trajectory_score_year_scenario') }}
    where year = 2045
      and scenario_id = 'baseline_ml_dynamic_risk'

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

joined as (

    select
        coalesce(s.country_iso3, m.country_iso3) as country_iso3,
        d.country_name,
        d.region,
        d.subregion,
        d.income_group,
        d.is_sovereign,

        s.trajectory_score_static_2045,
        m.trajectory_score_ml_2045,
        m.trajectory_score_ml_2045 - s.trajectory_score_static_2045 as trajectory_score_delta_ml_minus_static,

        s.trajectory_rank_static_2045,
        m.trajectory_rank_ml_2045,
        s.trajectory_rank_static_2045 - m.trajectory_rank_ml_2045 as trajectory_rank_delta_static_minus_ml,

        s.forecast_score_completeness_static,
        m.forecast_score_completeness_ml
    from static_2045 s
    full outer join ml_2045 m
      on s.country_iso3 = m.country_iso3
    left join country_dim d
      on coalesce(s.country_iso3, m.country_iso3) = d.country_iso3

)

select *
from joined
