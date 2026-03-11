{{ config(
    materialized = 'table'
) }}

with base as (

    select
        upper(trim(source_alpha2)) as source_alpha2,
        year,
        variable,
        percentile,
        safe_cast(value as float64) as value
    from {{ ref('wid_inequality_extract') }}
    where year >= 1950

),

pivoted as (

    select
        source_alpha2,
        year,

        max(case
            when variable = 'gptincj992'
             and percentile = 'p0p100'
            then value
        end) as gini_income,

        max(case
            when variable = 'sptincj992'
             and percentile = 'p0p50'
            then value
        end) as bottom50_income_share_pct,

        max(case
            when variable = 'sptincj992'
             and percentile = 'p90p100'
            then value
        end) as top10_income_share_pct,

        max(case
            when variable = 'sptincj992'
             and percentile = 'p99p100'
            then value
        end) as top1_income_share_pct

    from base
    group by 1, 2

),

country_map as (

    select distinct
        upper(trim(country_iso2)) as country_iso2,
        upper(trim(country_iso3)) as country_iso3
    from {{ ref('dim_country') }}
    where country_iso2 is not null
      and country_iso3 is not null

)

select
    m.country_iso3,
    p.year,
    p.gini_income,
    p.bottom50_income_share_pct,
    p.top10_income_share_pct,
    p.top1_income_share_pct
from pivoted p
join country_map m
    on p.source_alpha2 = m.country_iso2