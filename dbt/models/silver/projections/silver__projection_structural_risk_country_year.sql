{{ config(materialized='table') }}

with forecast_years as (

    select
        year
    from {{ ref('dim_year') }}
    where year between 2024 and 2045

),

countries as (

    select
        country_iso3
    from {{ ref('dim_country') }}
    where country_iso3 is not null

),

indicators as (

    select 'vdem_liberal_democracy_index' as indicator_name
    union all
    select 'adaptation_readiness' as indicator_name
    union all
    select 'climate_vulnerability' as indicator_name
    union all
    select 'conflict_severity' as indicator_name

),

contract_rows as (

    select
        c.country_iso3,
        y.year,
        'baseline_static_risk' as scenario_id,
        i.indicator_name,
        cast(null as float64) as projected_value,
        'world2045_sprint1_contract_placeholder' as projection_source,
        'ml_placeholder' as forecast_method,
        'sprint1_contract_v1' as model_version,
        current_timestamp() as created_at
    from countries c
    cross join forecast_years y
    cross join indicators i

)

select *
from contract_rows
