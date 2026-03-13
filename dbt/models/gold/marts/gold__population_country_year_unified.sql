with base as (

    select
        country_iso3,
        cast(year as int64) as year,
        cast(population_total as float64) as population_total,
        cast(population_male as float64) as population_male,
        cast(population_female as float64) as population_female
    from {{ ref('silver__fact_population_country_year') }}

),

final as (

    select
        country_iso3,
        year,
        population_total,
        population_male,
        population_female,

        case
            when year <= 2023 then 'observed'
            else 'projected'
        end as data_status,

        case
            when year <= 2023 then null
            else 'Medium'
        end as projection_variant,

        'WPP_2024' as source_system,
        current_timestamp() as updated_at
    from base

)

select *
from final