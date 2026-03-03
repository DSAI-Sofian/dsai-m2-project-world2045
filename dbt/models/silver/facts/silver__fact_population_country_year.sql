{{ config(
    materialized="incremental",
    incremental_strategy="merge",
    unique_key=["country_iso3","year"],
    on_schema_change="append_new_columns",
    partition_by={
      "field": "year",
      "data_type": "int64",
      "range": {"start": 1950, "end": 2101, "interval": 1}
    },
    cluster_by=["country_iso3"]
) }}

{% set pop_mult = 1000 %}
{% set reprocess_years = 5 %}

WITH src AS (

  SELECT
    country_iso3,
    CAST(year AS INT64) AS year,
    variant,
    CAST(pop_total_thousands AS FLOAT64) AS pop_total_thousands,
    CAST(pop_male_thousands  AS FLOAT64) AS pop_male_thousands,
    CAST(pop_female_thousands AS FLOAT64) AS pop_female_thousands

  FROM {{ source('world-population-projections', 'bronze__wpp2024__population_standard') }}

  WHERE variant = 'Medium'
    AND country_iso3 IS NOT NULL
    AND year IS NOT NULL

  {% if is_incremental() %}
    AND year >= (
      SELECT COALESCE(MAX(year), 1950) - {{ reprocess_years }}
      FROM {{ this }}
    )
  {% endif %}

)

SELECT
  country_iso3,
  year,
  pop_total_thousands * {{ pop_mult }} AS population_total,
  pop_male_thousands  * {{ pop_mult }} AS population_male,
  pop_female_thousands * {{ pop_mult }} AS population_female,
  CURRENT_TIMESTAMP() AS updated_at
FROM src