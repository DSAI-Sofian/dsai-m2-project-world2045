{{ config(materialized='table', cluster_by=['scope_type']) }}

with base as (

    select
        *
    from {{ ref('gold__scenario_delta_country_2045') }}
    where is_sovereign = true

),

overall as (

    select
        'global' as scope_type,
        cast(null as string) as scope_name,
        count(*) as country_count,
        avg(trajectory_score_delta_ml_minus_static) as avg_score_delta,
        min(trajectory_score_delta_ml_minus_static) as min_score_delta,
        max(trajectory_score_delta_ml_minus_static) as max_score_delta,
        avg(trajectory_rank_delta_static_minus_ml) as avg_rank_delta
    from base

),

by_region as (

    select
        'region' as scope_type,
        region as scope_name,
        count(*) as country_count,
        avg(trajectory_score_delta_ml_minus_static) as avg_score_delta,
        min(trajectory_score_delta_ml_minus_static) as min_score_delta,
        max(trajectory_score_delta_ml_minus_static) as max_score_delta,
        avg(trajectory_rank_delta_static_minus_ml) as avg_rank_delta
    from base
    where region is not null
    group by region

)

select * from overall
union all
select * from by_region
