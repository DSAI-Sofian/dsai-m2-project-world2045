{{ config(
    materialized='table',
    cluster_by=['country_iso3']
) }}

with base as (

    select
        country_iso3,
        year,
        indicator_id,
        safe_cast(value as float64) as value
    from {{ ref('silver__wdi_country_year_long') }}
    where country_iso3 is not null
      and year between 1960 and 2023
      and indicator_id in (
          'SP.DYN.LE00.IN',        -- life expectancy at birth, total (years)
          'SP.DYN.IMRT.IN',        -- infant mortality rate (per 1,000 live births)
          'SH.DYN.MORT',           -- mortality rate, under-5 (per 1,000)
          'SH.STA.MMRT',           -- maternal mortality ratio (per 100,000 live births)
          'SH.MED.PHYS.ZS',        -- physicians (per 1,000 people)
          'SH.MED.BEDS.ZS',        -- hospital beds (per 1,000 people)
          'SH.XPD.CHEX.GD.ZS',     -- current health expenditure (% of GDP)

          'SE.PRM.NENR',           -- school enrollment, primary (% net)
          'SE.SEC.NENR',           -- school enrollment, secondary (% net)
          'SE.TER.ENRR',           -- school enrollment, tertiary (% gross)
          'SE.XPD.TOTL.GD.ZS',     -- government expenditure on education, total (% of GDP)

          'SI.POV.GINI',           -- gini index
          'SI.DST.FRST.20',        -- income share held by lowest 20%
          'SL.UEM.TOTL.ZS',        -- unemployment, total (% of total labor force)
          'SL.UEM.1524.ZS'         -- unemployment, youth total (% ages 15-24)
      )

),

deduped as (

    select
        country_iso3,
        year,
        indicator_id,
        max(value) as value
    from base
    group by 1, 2, 3

),

pivoted as (

    select
        country_iso3,
        year,

        max(case when indicator_id = 'SP.DYN.LE00.IN' then value end) as life_expectancy_years,
        max(case when indicator_id = 'SP.DYN.IMRT.IN' then value end) as infant_mortality_per_1000,
        max(case when indicator_id = 'SH.DYN.MORT' then value end) as under5_mortality_per_1000,
        max(case when indicator_id = 'SH.STA.MMRT' then value end) as maternal_mortality_per_100k,
        max(case when indicator_id = 'SH.MED.PHYS.ZS' then value end) as physicians_per_1000,
        max(case when indicator_id = 'SH.MED.BEDS.ZS' then value end) as hospital_beds_per_1000,
        max(case when indicator_id = 'SH.XPD.CHEX.GD.ZS' then value end) as health_expenditure_pct_gdp,

        max(case when indicator_id = 'SE.PRM.NENR' then value end) as primary_enrollment_pct,
        max(case when indicator_id = 'SE.SEC.NENR' then value end) as secondary_enrollment_pct,
        max(case when indicator_id = 'SE.TER.ENRR' then value end) as tertiary_enrollment_pct,
        max(case when indicator_id = 'SE.XPD.TOTL.GD.ZS' then value end) as education_expenditure_pct_gdp,

        max(case when indicator_id = 'SI.POV.GINI' then value end) as gini_index,
        max(case when indicator_id = 'SI.DST.FRST.20' then value end) as income_share_lowest_20_pct,
        max(case when indicator_id = 'SL.UEM.TOTL.ZS' then value end) as unemployment_pct,
        max(case when indicator_id = 'SL.UEM.1524.ZS' then value end) as youth_unemployment_pct

    from deduped
    group by 1, 2

)

select *
from pivoted