{{ config(
    materialized = 'table',
    cluster_by = ['year']
) }}

with base as (

    select
        year,
        population_total,
        gdp_current_usd,
        life_expectancy_years,
        secondary_enrollment_gross_pct,
        poverty_headcount_pct,
        vdem_liberal_democracy_index
    from {{ ref('gold__mart_world2045_features_country_year') }}

)

select
    year,
    count(*) as rows_total,

    countif(population_total is not null) as population_rows,
    countif(gdp_current_usd is not null) as gdp_rows,
    countif(life_expectancy_years is not null) as life_expectancy_rows,
    countif(secondary_enrollment_gross_pct is not null) as education_rows,
    countif(poverty_headcount_pct is not null) as inequality_rows,
    countif(vdem_liberal_democracy_index is not null) as governance_rows,

    round(100 * safe_divide(countif(population_total is not null), count(*)), 2) as population_coverage_pct,
    round(100 * safe_divide(countif(gdp_current_usd is not null), count(*)), 2) as gdp_coverage_pct,
    round(100 * safe_divide(countif(life_expectancy_years is not null), count(*)), 2) as life_expectancy_coverage_pct,
    round(100 * safe_divide(countif(secondary_enrollment_gross_pct is not null), count(*)), 2) as education_coverage_pct,
    round(100 * safe_divide(countif(poverty_headcount_pct is not null), count(*)), 2) as inequality_coverage_pct,
    round(100 * safe_divide(countif(vdem_liberal_democracy_index is not null), count(*)), 2) as governance_coverage_pct

from base
group by year