{{ config(
    materialized = 'table'
) }}

with wdi_long as (

    select
        country_iso3,
        year,
        indicator_id,
        value
    from {{ ref('silver__wdi_country_year_long') }}
    where indicator_id in (
        'SE.SEC.ENRR'
    )

),

pivoted as (

    select
        country_iso3,
        year,

        max(case
            when indicator_id = 'SE.SEC.ENRR' then value
        end) as secondary_enrollment_gross_pct

    from wdi_long
    group by 1, 2

),

spine as (

    select
        country_iso3,
        year
    from {{ ref('fact_country_year_spine') }}
    where year <= 2045

)

select
    s.country_iso3,
    s.year,
    e.secondary_enrollment_gross_pct

from spine s
left join pivoted e
    on s.country_iso3 = e.country_iso3
   and s.year = e.year