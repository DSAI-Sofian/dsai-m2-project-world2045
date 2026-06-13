{{ config(materialized='table') }}

with panel_spine as (

    select
        country_iso3,
        year
    from {{ ref('fact_country_year_spine') }}
    where year between 1995 and 2023

),

governance as (

    select
        country_iso3,
        year,
        cast(vdem_liberal_democracy_index as float64) as vdem_liberal_democracy_index
    from {{ ref('silver__fact_governance_country_year') }}

),

climate as (

    select
        country_iso3,
        year,
        cast(adaptation_readiness as float64) as adaptation_readiness,
        cast(climate_vulnerability as float64) as climate_vulnerability
    from {{ ref('silver__fact_climate_risk_country_year') }}

),

wide_panel as (

    select
        s.country_iso3,
        s.year,
        g.vdem_liberal_democracy_index,
        c.adaptation_readiness,
        c.climate_vulnerability
    from panel_spine s
    left join governance g
        on s.country_iso3 = g.country_iso3
       and s.year = g.year
    left join climate c
        on s.country_iso3 = c.country_iso3
       and s.year = c.year

),

long_panel as (

    select country_iso3, year, 'vdem_liberal_democracy_index' as indicator_name, vdem_liberal_democracy_index as indicator_value from wide_panel
    union all
    select country_iso3, year, 'adaptation_readiness' as indicator_name, adaptation_readiness as indicator_value from wide_panel
    union all
    select country_iso3, year, 'climate_vulnerability' as indicator_name, climate_vulnerability as indicator_value from wide_panel

),

features as (

    select
        country_iso3,
        year,
        indicator_name,
        indicator_value,

        lag(indicator_value, 1) over (
            partition by country_iso3, indicator_name
            order by year
        ) as prev_year_value,

        avg(indicator_value) over (
            partition by country_iso3, indicator_name
            order by year
            rows between 3 preceding and 1 preceding
        ) as rolling_mean_3y,

        avg(indicator_value) over (
            partition by country_iso3, indicator_name
            order by year
            rows between 5 preceding and 1 preceding
        ) as rolling_mean_5y,

        lag(indicator_value, 1) over (
            partition by country_iso3, indicator_name
            order by year
        )
        -
        lag(indicator_value, 4) over (
            partition by country_iso3, indicator_name
            order by year
        ) as change_3y,

        lag(indicator_value, 1) over (
            partition by country_iso3, indicator_name
            order by year
        )
        -
        lag(indicator_value, 6) over (
            partition by country_iso3, indicator_name
            order by year
        ) as change_5y
    from long_panel

)

select
    country_iso3,
    year,
    indicator_name,
    indicator_value,
    prev_year_value,
    rolling_mean_3y,
    rolling_mean_5y,
    change_3y,
    change_5y,
    indicator_value is null as is_indicator_missing,
    prev_year_value is null as is_prev_year_missing,
    rolling_mean_3y is null as is_rolling_mean_3y_missing,
    rolling_mean_5y is null as is_rolling_mean_5y_missing,
    current_timestamp() as created_at
from features
