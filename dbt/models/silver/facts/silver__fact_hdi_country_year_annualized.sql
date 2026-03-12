{{ config(
    materialized = 'table'
) }}

with spine as (

    select
        country_iso3,
        year
    from {{ ref('fact_country_year_spine') }}
    where year between 1950 and 2045

),

observed as (

    select
        country_iso3,
        year,
        hdi
    from {{ ref('silver__fact_hdi_country_year') }}

),

joined as (

    select
        s.country_iso3,
        s.year,
        o.hdi as hdi_observed
    from spine s
    left join observed o
        on s.country_iso3 = o.country_iso3
       and s.year = o.year

),

anchors as (

    select
        country_iso3,
        year,
        hdi_observed,

        last_value(hdi_observed ignore nulls)
            over (
                partition by country_iso3
                order by year
            ) as prev_hdi,

        last_value(
            case when hdi_observed is not null then year end
            ignore nulls
        ) over (
            partition by country_iso3
            order by year
        ) as prev_year,

        first_value(hdi_observed ignore nulls)
            over (
                partition by country_iso3
                order by year desc
            ) as next_hdi,

        first_value(
            case when hdi_observed is not null then year end
            ignore nulls
        ) over (
            partition by country_iso3
            order by year desc
        ) as next_year

    from joined

),

interpolated as (

    select
        country_iso3,
        year,

        case
            when hdi_observed is not null
                then hdi_observed

            when prev_hdi is not null
             and next_hdi is not null
             and next_year > prev_year

                then prev_hdi
                     + (next_hdi - prev_hdi)
                       * safe_divide(year - prev_year, next_year - prev_year)

            else null
        end as hdi,

        hdi_observed is not null as hdi_is_observed,

        case
            when hdi_observed is null
             and prev_hdi is not null
             and next_hdi is not null
             and year > prev_year
             and year < next_year
                then true
            else false
        end as hdi_is_interpolated

    from anchors

)

select
    country_iso3,
    year,
    hdi,
    hdi_is_observed,
    hdi_is_interpolated

from interpolated