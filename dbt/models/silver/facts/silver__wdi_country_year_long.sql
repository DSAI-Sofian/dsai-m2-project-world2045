{{ config(
    materialized='table'
) }}

with src as (

    select *
    from {{ source('world-development-indicators', 'bronze__wdi_country_year_long') }}

),

typed as (

    select
        cast(source_system as string) as source_system,
        cast(dataset_code as string) as dataset_code,
        upper(cast(country_id as string)) as country_id,
        cast(country_name as string) as country_name,
        upper(cast(iso3c as string)) as raw_country_code,
        cast(year as int64) as year,
        cast(indicator_id as string) as indicator_id,
        cast(indicator_name as string) as indicator_name,
        safe_cast(value as numeric) as value,
        cast(unit as string) as unit,
        cast(obs_status as string) as obs_status,
        cast(decimal as int64) as decimal,
        cast(ingested_at as timestamp) as ingested_at
    from src
    where year is not null
      and indicator_id is not null

),

country_dim as (

    select
        upper(country_iso3) as country_iso3,
        upper(country_iso2) as country_iso2
    from {{ ref('dim_country') }}

),

conformed as (

    select
        t.source_system,
        t.dataset_code,
        t.country_id,
        t.country_name,

        case
            when length(t.raw_country_code) = 3 and d3.country_iso3 is not null then d3.country_iso3
            when length(t.raw_country_code) = 2 and d2.country_iso3 is not null then d2.country_iso3
            else null
        end as country_iso3,

        t.year,
        t.indicator_id,
        t.indicator_name,
        t.value,
        t.unit,
        t.obs_status,
        t.decimal,
        t.ingested_at

    from typed t
    left join country_dim d3
        on t.raw_country_code = d3.country_iso3
    left join country_dim d2
        on t.raw_country_code = d2.country_iso2

)

select *
from conformed
where country_iso3 is not null