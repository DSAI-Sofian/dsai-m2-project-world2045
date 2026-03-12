{{ config(
    materialized = 'table'
) }}

with spine as (

    select
        country_iso3,
        year
    from {{ ref('fact_country_year_spine') }}
    where year between 1950 and 2045

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
        safe_cast(value as float64) as value
    from {{ ref('silver__wdi_country_year_long') }}
    where indicator_id in (
        'NY.GDP.MKTP.CD',
        'NY.GDP.PCAP.CD',
        'NY.GDP.MKTP.KD.ZG',
        'FP.CPI.TOTL.ZG',
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
        max(case when indicator_id = 'FP.CPI.TOTL.ZG' then value end) as inflation_cpi_pct,
        max(case when indicator_id = 'IT.NET.USER.ZS' then value end) as internet_users_pct,
        max(case when indicator_id = 'EG.ELC.ACCS.ZS' then value end) as access_to_electricity_pct,
        max(case when indicator_id = 'SI.POV.LMIC' then value end) as poverty_headcount_pct

    from wdi_long
    group by 1, 2

),

wdi_features as (

    select
        country_iso3,
        year,
        life_expectancy_years,
        infant_mortality_per_1000,
        under5_mortality_per_1000,
        maternal_mortality_per_100k,
        physicians_per_1000,
        hospital_beds_per_1000,
        health_expenditure_pct_gdp,
        primary_enrollment_pct,
        secondary_enrollment_pct,
        tertiary_enrollment_pct,
        education_expenditure_pct_gdp,
        gini_index,
        income_share_lowest_20_pct,
        unemployment_pct,
        youth_unemployment_pct
    from {{ ref('silver__wdi_country_year_features') }}

),

education as (

    select
        country_iso3,
        year,
        secondary_enrollment_gross_pct
    from {{ ref('silver__fact_education_country_year') }}

),

hdi as (

    select
        country_iso3,
        year,
        hdi,
        hdi_is_observed,
        hdi_is_interpolated
    from {{ ref('silver__fact_hdi_country_year_annualized') }}

),

inequality as (

    select
        country_iso3,
        year,
        gini_income,
        bottom50_income_share_pct,
        top10_income_share_pct,
        top1_income_share_pct
    from {{ ref('silver__fact_inequality_country_year') }}

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

),

climate as (

    select
        country_iso3,
        year,
        ndgain_index,
        climate_vulnerability,
        adaptation_readiness
    from {{ ref('silver__fact_climate_risk_country_year') }}

),

conflict as (

    select
        country_iso3,
        year,
        battle_deaths,
        conflict_incidence,
        interstate_conflict,
        civil_conflict,
        internationalized_conflict,
        war_intensity
    from {{ ref('silver__fact_conflict_country_year') }}

)

select
    s.country_iso3,
    s.year,

    p.population_total,

    w.gdp_current_usd,
    w.gdp_per_capita_current_usd,
    w.gdp_growth_pct,
    wf.unemployment_pct,
    wf.youth_unemployment_pct,
    w.inflation_cpi_pct,

    wf.life_expectancy_years,
    wf.infant_mortality_per_1000,
    wf.under5_mortality_per_1000,
    wf.maternal_mortality_per_100k,
    wf.physicians_per_1000,
    wf.hospital_beds_per_1000,
    wf.health_expenditure_pct_gdp,

    wf.primary_enrollment_pct,
    wf.secondary_enrollment_pct,
    wf.tertiary_enrollment_pct,
    wf.education_expenditure_pct_gdp,
    e.secondary_enrollment_gross_pct,

    wf.gini_index,
    wf.income_share_lowest_20_pct,

    h.hdi,
    h.hdi_is_observed,
    h.hdi_is_interpolated,
    i.gini_income,
    i.bottom50_income_share_pct,
    i.top10_income_share_pct,
    i.top1_income_share_pct,

    w.internet_users_pct,
    w.access_to_electricity_pct,
    w.poverty_headcount_pct,

    g.vdem_liberal_democracy_index,
    g.vdem_electoral_democracy_index,
    g.vdem_judicial_constraints_index,
    g.vdem_civil_liberties_index,

    c.ndgain_index,
    c.climate_vulnerability,
    c.adaptation_readiness,

    f.battle_deaths,
    f.conflict_incidence,
    f.interstate_conflict,
    f.civil_conflict,
    f.internationalized_conflict,
    f.war_intensity,

    p.population_total is not null as population_available,
    w.gdp_current_usd is not null as gdp_available,
    wf.life_expectancy_years is not null as life_expectancy_available,
    wf.secondary_enrollment_pct is not null as secondary_enrollment_available,
    w.internet_users_pct is not null as internet_available,

    (
        wf.gini_index is not null
        or wf.income_share_lowest_20_pct is not null
        or i.gini_income is not null
        or i.bottom50_income_share_pct is not null
        or i.top10_income_share_pct is not null
        or i.top1_income_share_pct is not null
    ) as inequality_available,

    wf.health_expenditure_pct_gdp is not null as health_available,
    h.hdi is not null as hdi_available,

    g.country_iso3 is not null as governance_available,
    g.vdem_liberal_democracy_index is not null as vdem_liberal_democracy_available,
    g.vdem_electoral_democracy_index is not null as vdem_electoral_democracy_available,
    g.vdem_judicial_constraints_index is not null as vdem_judicial_constraints_available,
    g.vdem_civil_liberties_index is not null as vdem_civil_liberties_available,

    c.ndgain_index is not null as climate_available,
    f.conflict_incidence is not null as conflict_available

from spine s
left join population p
    on s.country_iso3 = p.country_iso3
   and s.year = p.year
left join wdi_pivot w
    on s.country_iso3 = w.country_iso3
   and s.year = w.year
left join wdi_features wf
    on s.country_iso3 = wf.country_iso3
   and s.year = wf.year
left join education e
    on s.country_iso3 = e.country_iso3
   and s.year = e.year
left join hdi h
    on s.country_iso3 = h.country_iso3
   and s.year = h.year
left join inequality i
    on s.country_iso3 = i.country_iso3
   and s.year = i.year
left join governance g
    on s.country_iso3 = g.country_iso3
   and s.year = g.year
left join climate c
    on s.country_iso3 = c.country_iso3
   and s.year = c.year
left join conflict f
    on s.country_iso3 = f.country_iso3
   and s.year = f.year