{{ config(
    materialized = 'table'
) }}

with spine as (

    select
        country_iso3,
        year
    from {{ ref('fact_country_year_spine') }}
    where year <= 2045

),

inequality as (

    select
        country_iso3,
        year,
        max(safe_cast(value as float64)) as poverty_headcount_pct
    from {{ ref('silver__wdi_country_year_long') }}
    where indicator_id = 'SI.POV.LMIC'
    group by 1, 2

)

select
    s.country_iso3,
    s.year,
    i.poverty_headcount_pct

from spine s
left join inequality i
    on s.country_iso3 = i.country_iso3
   and s.year = i.year