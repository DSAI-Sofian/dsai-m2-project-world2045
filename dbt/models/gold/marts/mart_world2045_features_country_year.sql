{{ config(materialized="table") }}

with spine as (

    select
        country_iso3,
        year
    from {{ ref('fact_country_year_spine') }}
    where year <= 2045

),

population as (

    select
        country_iso3,
        year,
        population_total
    from {{ ref('silver__fact_population_country_year') }}

),

wdi_long as (

    select
        country_iso3,
        year,
        indicator_id,
        value
    from {{ ref('silver__wdi_country_year_long') }}

),

wdi_pivot as (

    select
        country_iso3,
        year,

        max(case when indicator_id = 'NY.GDP.MKTP.CD' then value end) as gdp_current_usd,
        max(case when indicator_id = 'NY.GDP.PCAP.CD' then value end) as gdp_per_capita_current_usd,
        max(case when indicator_id = 'NY.GDP.MKTP.KD.ZG' then value end) as gdp_growth_pct,
        max(case when indicator_id = 'SL.UEM.TOTL.ZS' then value end) as unemployment_pct,
        max(case when indicator_id = 'FP.CPI.TOTL.ZG' then value end) as inflation_cpi_pct,
        max(case when indicator_id = 'SP.DYN.LE00.IN' then value end) as life_expectancy_years,
        max(case when indicator_id = 'SH.DYN.MORT' then value end) as under5_mortality_per_1000,
        max(case when indicator_id = 'SE.SEC.ENRR' then value end) as secondary_enrollment_gross_pct,
        max(case when indicator_id = 'IT.NET.USER.ZS' then value end) as internet_users_pct,
        max(case when indicator_id = 'EG.ELC.ACCS.ZS' then value end) as access_to_electricity_pct,
        max(case when indicator_id = 'SI.POV.LMIC' then value end) as poverty_headcount_pct

    from wdi_long
    group by 1, 2

)

select
    s.country_iso3,
    s.year,

    p.population_total,

    w.gdp_current_usd,
    w.gdp_per_capita_current_usd,
    w.gdp_growth_pct,
    w.unemployment_pct,
    w.inflation_cpi_pct,
    w.life_expectancy_years,
    w.under5_mortality_per_1000,
    w.secondary_enrollment_gross_pct,
    w.internet_users_pct,
    w.access_to_electricity_pct,
    w.poverty_headcount_pct

from spine s
left join population p
    on s.country_iso3 = p.country_iso3
   and s.year = p.year
left join wdi_pivot w
    on s.country_iso3 = w.country_iso3
   and s.year = w.year