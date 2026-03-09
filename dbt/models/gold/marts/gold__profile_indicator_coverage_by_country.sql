{{ config(
    materialized = 'table'
) }}

with base as (

    select
        country_iso3,
        population_total,
        gdp_current_usd,
        life_expectancy_years,
        secondary_enrollment_gross_pct,
        poverty_headcount_pct,
        vdem_liberal_democracy_index
    from {{ ref('gold__mart_world2045_features_analytic_1960_2023') }}

)

select
    country_iso3,
    count(*) as year_rows_total,

    countif(population_total is not null) as population_years,
    countif(gdp_current_usd is not null) as gdp_years,
    countif(life_expectancy_years is not null) as life_expectancy_years_count,
    countif(secondary_enrollment_gross_pct is not null) as education_years,
    countif(poverty_headcount_pct is not null) as inequality_years,
    countif(vdem_liberal_democracy_index is not null) as governance_years,

    round(100 * safe_divide(countif(population_total is not null), count(*)), 2) as population_coverage_pct,
    round(100 * safe_divide(countif(gdp_current_usd is not null), count(*)), 2) as gdp_coverage_pct,
    round(100 * safe_divide(countif(life_expectancy_years is not null), count(*)), 2) as life_expectancy_coverage_pct,
    round(100 * safe_divide(countif(secondary_enrollment_gross_pct is not null), count(*)), 2) as education_coverage_pct,
    round(100 * safe_divide(countif(poverty_headcount_pct is not null), count(*)), 2) as inequality_coverage_pct,
    round(100 * safe_divide(countif(vdem_liberal_democracy_index is not null), count(*)), 2) as governance_coverage_pct,

    countif(
        population_total is not null
        and gdp_current_usd is not null
        and life_expectancy_years is not null
        and vdem_liberal_democracy_index is not null
    ) as core_complete_years,

    round(
        100 * safe_divide(
            countif(
                population_total is not null
                and gdp_current_usd is not null
                and life_expectancy_years is not null
                and vdem_liberal_democracy_index is not null
            ),
            count(*)
        ),
        2
    ) as core_complete_coverage_pct

from base
group by country_iso3