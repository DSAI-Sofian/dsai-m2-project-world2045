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
    where indicator_id in (
        'NY.GDP.MKTP.CD',
        'NY.GDP.PCAP.CD',
        'NY.GDP.MKTP.KD.ZG',
        'SL.UEM.TOTL.ZS',
        'FP.CPI.TOTL.ZG',
        'SP.DYN.LE00.IN',
        'SH.DYN.MORT',
        'IT.NET.USER.ZS',
        'EG.ELC.ACCS.ZS',
        'SI.POV.LMIC'
    )

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
        max(case when indicator_id = 'IT.NET.USER.ZS' then value end) as internet_users_pct,
        max(case when indicator_id = 'EG.ELC.ACCS.ZS' then value end) as access_to_electricity_pct,
        max(case when indicator_id = 'SI.POV.LMIC' then value end) as poverty_headcount_pct

    from wdi_long
    group by 1, 2

),

education as (

    select
        country_iso3,
        year,
        secondary_enrollment_gross_pct
    from {{ ref('silver__fact_education_country_year') }}

),

governance as (

    select
        country_iso3,
        year,
        vdem_liberal_democracy_index,
        vdem_electoral_democracy_index,
        vdem_judicial_constraints_index,
        vdem_civil_liberties_index
    from {{ ref('silver__fact_governance_country_year') }}

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
    e.secondary_enrollment_gross_pct,
    w.internet_users_pct,
    w.access_to_electricity_pct,
    w.poverty_headcount_pct,

    g.vdem_liberal_democracy_index,
    g.vdem_electoral_democracy_index,
    g.vdem_judicial_constraints_index,
    g.vdem_civil_liberties_index,

    p.population_total is not null as population_available,
    w.gdp_current_usd is not null as gdp_available,
    w.life_expectancy_years is not null as life_expectancy_available,
    e.secondary_enrollment_gross_pct is not null as secondary_enrollment_available,
    w.internet_users_pct is not null as internet_available,

    g.country_iso3 is not null as governance_available,
    g.vdem_liberal_democracy_index is not null as vdem_liberal_democracy_available,
    g.vdem_electoral_democracy_index is not null as vdem_electoral_democracy_available,
    g.vdem_judicial_constraints_index is not null as vdem_judicial_constraints_available,
    g.vdem_civil_liberties_index is not null as vdem_civil_liberties_available

from spine s
left join population p
    on s.country_iso3 = p.country_iso3
   and s.year = p.year
left join wdi_pivot w
    on s.country_iso3 = w.country_iso3
   and s.year = w.year
left join education e
    on s.country_iso3 = e.country_iso3
   and s.year = e.year
left join governance g
    on s.country_iso3 = g.country_iso3
   and s.year = g.year