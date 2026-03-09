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

health as (

    select
        country_iso3,
        year,
        max(case when indicator_id = 'SP.DYN.LE00.IN' then safe_cast(value as float64) end) as life_expectancy_years,
        max(case when indicator_id = 'SH.DYN.MORT' then safe_cast(value as float64) end) as under5_mortality_per_1000
    from {{ ref('silver__wdi_country_year_long') }}
    where indicator_id in (
        'SP.DYN.LE00.IN',
        'SH.DYN.MORT'
    )
    group by 1, 2

)

select
    s.country_iso3,
    s.year,
    h.life_expectancy_years,
    h.under5_mortality_per_1000

from spine s
left join health h
    on s.country_iso3 = h.country_iso3
   and s.year = h.year