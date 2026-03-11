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

wdi_inequality as (

    select
        country_iso3,
        year,
        max(safe_cast(value as float64)) as poverty_headcount_pct
    from {{ ref('silver__wdi_country_year_long') }}
    where indicator_id = 'SI.POV.LMIC'
    group by 1, 2

),

wid_inequality as (

    select
        country_iso3,
        year,
        gini_income,
        bottom50_income_share_pct,
        top10_income_share_pct,
        top1_income_share_pct
    from {{ ref('silver__wid_inequality_country_year') }}

)

select
    s.country_iso3,
    s.year,
    wdi.poverty_headcount_pct,
    wid.gini_income,
    wid.bottom50_income_share_pct,
    wid.top10_income_share_pct,
    wid.top1_income_share_pct

from spine s
left join wdi_inequality wdi
    on s.country_iso3 = wdi.country_iso3
   and s.year = wdi.year
left join wid_inequality wid
    on s.country_iso3 = wid.country_iso3
   and s.year = wid.year