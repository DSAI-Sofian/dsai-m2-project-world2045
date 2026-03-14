{{ config(materialized='table') }}

with anchors as (

    select
        country_iso3,
        cast(year as int64) as year,
        scenario_name,
        model_name,
        cast(gdp_real_billion_usd as float64) as gdp_real_billion_usd
    from {{ ref('silver__projection_gdp_country_year') }}
    where year between 2025 and 2045

),

anchor_pairs as (

    select
        a.country_iso3,
        a.scenario_name,
        a.model_name,
        a.year as start_year,
        b.year as end_year,
        a.gdp_real_billion_usd as start_gdp,
        b.gdp_real_billion_usd as end_gdp
    from anchors a
    join anchors b
      on a.country_iso3 = b.country_iso3
     and a.scenario_name = b.scenario_name
     and a.model_name = b.model_name
     and b.year = a.year + 5

),

expanded as (

    select
        p.country_iso3,
        y as year,
        p.scenario_name,
        p.model_name,
        case
            when y = p.start_year then p.start_gdp
            when y = p.end_year then p.end_gdp
            else p.start_gdp
                 + ((p.end_gdp - p.start_gdp) * (y - p.start_year) / (p.end_year - p.start_year))
        end as gdp_real_billion_usd
    from anchor_pairs p,
    unnest(generate_array(p.start_year, p.end_year)) as y

),

deduplicated as (

    select *
    from expanded
    qualify row_number() over (
        partition by country_iso3, year
        order by year
    ) = 1

)

select
    country_iso3,
    cast(year as int64) as year,
    scenario_name,
    model_name,
    cast(gdp_real_billion_usd as float64) as gdp_real_billion_usd
from deduplicated
where year between 2025 and 2045
order by country_iso3, year