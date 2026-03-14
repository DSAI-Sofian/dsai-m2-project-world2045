{{ config(materialized='view') }}

with source_data as (

    select *
    from {{ source('bronze', 'bronze__ssp_gdp_projection_raw') }}

)

select
    trim(country_name) as country_name,
    cast(year as int64) as year,
    upper(trim(scenario)) as scenario_name,
    trim(model) as model_name,
    cast(gdp_real_billion_usd as float64) as gdp_real_billion_usd
from source_data
where cast(year as int64) >= 2025
  and gdp_real_billion_usd is not null