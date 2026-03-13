with population_projection as (

    select
        country_iso3,
        year,
        scenario_id,
        projection_variant,

        population_total_thousands,
        population_male_thousands,
        population_female_thousands,

        population_total_thousands * 1000 as population_total,
        population_male_thousands * 1000 as population_male,
        population_female_thousands * 1000 as population_female,

        fertility_rate,
        life_expectancy_birth_both,
        net_migrants_thousands,

        'WPP_2024' as source_system
    from {{ ref('silver__projection_population_country_year') }}

)

select *
from population_projection