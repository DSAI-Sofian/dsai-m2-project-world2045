with source as (

    select *
    from {{ source('world-population-projections', 'bronze__wpp2024__population_standard_raw') }}

),

base as (

    select
        country_iso3,
        cast(year as int64) as year,
        variant as projection_variant,

        'WPP' as scenario_family,
        'baseline' as scenario_id,
        'UN_WPP_2024' as projection_source,

        safe_cast(pop_total_jul_thousands as float64) as population_total_thousands,
        safe_cast(pop_male_jul_thousands as float64) as population_male_thousands,
        safe_cast(pop_female_jul_thousands as float64) as population_female_thousands,
        safe_cast(total_fertility_rate as float64) as fertility_rate,
        safe_cast(life_expectancy_birth_both as float64) as life_expectancy_birth_both,
        safe_cast(net_migrants_thousands as float64) as net_migrants_thousands,

        true as is_projection,
        current_timestamp() as ingestion_timestamp

    from source
    where year between 2024 and 2045
      and variant = 'Medium'
      and country_iso3 is not null
      and length(trim(country_iso3)) = 3

)

select *
from base