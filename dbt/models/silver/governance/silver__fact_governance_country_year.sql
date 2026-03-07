with source_data as (

    select
        upper(trim(country_iso3)) as country_iso3,
        cast(year as int64) as year,
        cast(vdem_liberal_democracy_index as float64) as vdem_liberal_democracy_index,
        cast(vdem_electoral_democracy_index as float64) as vdem_electoral_democracy_index,
        cast(vdem_judicial_constraints_index as float64) as vdem_judicial_constraints_index,
        cast(vdem_civil_liberties_index as float64) as vdem_civil_liberties_index
    from {{ source('bronze', 'vdem_country_year') }}

),

validated as (

    select
        s.country_iso3,
        s.year,
        s.vdem_liberal_democracy_index,
        s.vdem_electoral_democracy_index,
        s.vdem_judicial_constraints_index,
        s.vdem_civil_liberties_index
    from source_data s
    inner join {{ ref('dim_country') }} c
        on s.country_iso3 = c.country_iso3
    inner join {{ ref('dim_year') }} y
        on s.year = y.year

),

deduplicated as (

    select *
    from validated
    qualify row_number() over (
        partition by country_iso3, year
        order by year desc
    ) = 1

)

select
    country_iso3,
    year,
    vdem_liberal_democracy_index,
    vdem_electoral_democracy_index,
    vdem_judicial_constraints_index,
    vdem_civil_liberties_index
from deduplicated