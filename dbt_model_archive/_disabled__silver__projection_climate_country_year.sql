{{ config(
    materialized='table',
    partition_by={"field": "year", "data_type": "int64"},
    cluster_by=["country_iso3", "scenario_id", "metric_id"]
) }}

with source_data as (
    select *
    from {{ ref('bronze__climate_projection_country_year') }}
),

metric_union as (
    select
        country_iso3,
        cast(year as int64) as year,
        'CLIMATE_SCENARIO' as scenario_family,
        upper(scenario_id) as scenario_id,
        'CLIMATE_PROJECTION_SOURCE' as projection_source,
        'baseline' as projection_variant,
        cast(temperature_anomaly_c as float64) as value,
        'temperature_anomaly_c' as metric_id,
        true as is_projection,
        current_timestamp() as ingestion_timestamp
    from source_data
    where cast(year as int64) >= 2024
      and temperature_anomaly_c is not null

    union all

    select
        country_iso3,
        cast(year as int64) as year,
        'CLIMATE_SCENARIO' as scenario_family,
        upper(scenario_id) as scenario_id,
        'CLIMATE_PROJECTION_SOURCE' as projection_source,
        'baseline' as projection_variant,
        cast(precipitation_anomaly_pct as float64) as value,
        'precipitation_anomaly_pct' as metric_id,
        true as is_projection,
        current_timestamp() as ingestion_timestamp
    from source_data
    where cast(year as int64) >= 2024
      and precipitation_anomaly_pct is not null
)

select *
from metric_union
where country_iso3 is not null
  and year is not null
  and value is not null
