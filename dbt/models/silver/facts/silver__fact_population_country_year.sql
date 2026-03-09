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

WITH hist AS (

  SELECT
    iso3_alpha_code AS country_iso3,
    CAST(year AS INT64) AS year,
    variant,
    CAST(total_population_as_of_1_july_thousands AS FLOAT64) AS pop_total_thousands,
    CAST(male_population_as_of_1_july_thousands AS FLOAT64) AS pop_male_thousands,
    CAST(female_population_as_of_1_july_thousands AS FLOAT64) AS pop_female_thousands
  FROM {{ source('world-population-projections', 'bronze__wpp2024__f01_sheet1_clean') }}
  WHERE variant = 'Estimates'
    AND iso3_alpha_code IS NOT NULL
    AND year IS NOT NULL

  {% if is_incremental() %}
    AND CAST(year AS INT64) >= (
      SELECT COALESCE(MAX(year), 1950) - {{ reprocess_years }}
      FROM {{ this }}
    )
  {% endif %}

),

proj AS (

  SELECT
    iso3_alpha_code AS country_iso3,
    CAST(year AS INT64) AS year,
    variant,
    CAST(total_population_as_of_1_july_thousands AS FLOAT64) AS pop_total_thousands,
    CAST(male_population_as_of_1_july_thousands AS FLOAT64) AS pop_male_thousands,
    CAST(female_population_as_of_1_july_thousands AS FLOAT64) AS pop_female_thousands
  FROM {{ source('world-population-projections', 'bronze__wpp2024__f01_sheet2_clean') }}
  WHERE variant = 'Medium'
    AND iso3_alpha_code IS NOT NULL
    AND year IS NOT NULL

  {% if is_incremental() %}
    AND CAST(year AS INT64) >= (
      SELECT COALESCE(MAX(year), 1950) - {{ reprocess_years }}
      FROM {{ this }}
    )
  {% endif %}

),

src AS (

  SELECT * FROM hist
  UNION ALL
  SELECT * FROM proj

)

SELECT
  country_iso3,
  year,
  pop_total_thousands * {{ pop_mult }} AS population_total,
  pop_male_thousands  * {{ pop_mult }} AS population_male,
  pop_female_thousands * {{ pop_mult }} AS population_female,
  CURRENT_TIMESTAMP() AS updated_at
FROM src