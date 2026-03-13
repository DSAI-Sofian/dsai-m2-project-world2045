{{ config(
    materialized='table',
    partition_by={"field": "year", "data_type": "int64"},
    cluster_by=["country_iso3", "scenario_id", "metric_id"]
) }}

with source_data as (
    select *
    from {{ ref('bronze__ssp_gdp_projection') }}
),

metric_union as (
    select
        country_iso3,
        cast(year as int64) as year,
        'SSP' as scenario_family,
        upper(scenario_id) as scenario_id,
        'IIASA_SSP' as projection_source,
        'baseline' as projection_variant,
        cast(gdp_ppp as float64) as value,
        'gdp_ppp' as metric_id,
        true as is_projection,
        current_timestamp() as ingestion_timestamp
    from source_data
    where cast(year as int64) >= 2024
      and gdp_ppp is not null

    union all

    select
        country_iso3,
        cast(year as int64) as year,
        'SSP' as scenario_family,
        upper(scenario_id) as scenario_id,
        'IIASA_SSP' as projection_source,
        'baseline' as projection_variant,
        cast(gdp_per_capita as float64) as value,
        'gdp_per_capita' as metric_id,
        true as is_projection,
        current_timestamp() as ingestion_timestamp
    from source_data
    where cast(year as int64) >= 2024
      and gdp_per_capita is not null
)

select *
from metric_union
where country_iso3 is not null
  and year is not null
  and value is not null
