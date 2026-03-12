{{ config(
    materialized = 'table'
) }}

with base as (

    select
        trim(country) as country,
        cast(year as int64) as year,
        safe_cast(hdi as float64) as hdi
    from {{ ref('hdi_trends_table_long_clean') }}
    where year between 1990 and 2023

),

country_map as (

    select distinct
        country_name,
        country_iso3
    from {{ ref('dim_country') }}
    where country_name is not null
      and country_iso3 is not null

),

mapped as (

    select
        m.country_iso3,
        b.year,
        b.hdi
    from base b
    join country_map m
      on trim(b.country) = trim(m.country_name)

)

select
    country_iso3,
    year,
    hdi
from mapped