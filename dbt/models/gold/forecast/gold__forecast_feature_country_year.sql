{{ config(materialized='table') }}

with population_projection as (

    select *
    from {{ ref('silver__projection_population_country_year') }}

),

gdp_projection as (

    select
        country_iso3,
        year,
        gdp_real_billion_usd
    from {{ ref('silver__projection_gdp_country_year_annualized') }}

),

final as (

    select
        p.country_iso3,
        p.year,

        p.population_total_thousands,
        p.population_male_thousands,
        p.population_female_thousands,
        p.fertility_rate,
        p.life_expectancy_birth_both,
        p.net_migrants_thousands,

        g.gdp_real_billion_usd,

        case
            when p.population_total_thousands is not null
             and p.population_total_thousands != 0
             and g.gdp_real_billion_usd is not null
            then (g.gdp_real_billion_usd * 1000000) / p.population_total_thousands
            else null
        end as gdp_real_per_capita_usd

    from population_projection p
    left join gdp_projection g
      on p.country_iso3 = g.country_iso3
     and p.year = g.year

)

select *
from final