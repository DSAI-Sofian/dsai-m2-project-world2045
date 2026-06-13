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

static_placeholder as (

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

),

ml_climate_projection as (

    select
        upper(trim(country_iso3)) as country_iso3,
        cast(year as int64) as year,
        cast(scenario_id as string) as scenario_id,
        cast(indicator_name as string) as indicator_name,
        cast(projected_value as float64) as projected_value,
        cast(projection_source as string) as projection_source,
        cast(forecast_method as string) as forecast_method,
        cast(model_version as string) as model_version,
        current_timestamp() as created_at
    from {{ ref('ml_climate_vulnerability_projection_2024_2045') }}
    where scenario_id = 'baseline_ml_dynamic_risk'
      and indicator_name = 'climate_vulnerability'
      and year between 2024 and 2045
      and projected_value is not null

),

final as (

    select *
    from static_placeholder

    union all

    select *
    from ml_climate_projection

)

select *
from final
