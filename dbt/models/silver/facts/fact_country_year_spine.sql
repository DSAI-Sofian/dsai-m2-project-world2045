{{ config(
    materialized="table",
    partition_by={"field":"year","data_type":"int64","range":{"start":1950,"end":2101,"interval":1}},
    cluster_by=["country_iso3"],
    on_schema_change="sync_all_columns"
) }}

-- Canonical country-year spine
-- Grain: (country_iso3, year)
-- All domain facts should LEFT JOIN to this spine (or start from it).

WITH countries AS (
  SELECT
    country_iso3,
    valid_from_year,
    valid_to_year
  FROM {{ ref('dim_country') }}
),

years AS (
  SELECT year
  FROM {{ ref('dim_year') }}
),

spine AS (
  SELECT
    c.country_iso3,
    y.year,
    CASE
      WHEN c.valid_from_year IS NOT NULL AND y.year < c.valid_from_year THEN FALSE
      WHEN c.valid_to_year   IS NOT NULL AND y.year > c.valid_to_year   THEN FALSE
      ELSE TRUE
    END AS is_valid_entity_year
  FROM countries c
  CROSS JOIN years y
)

SELECT
  country_iso3,
  year,
  is_valid_entity_year,
  TO_HEX(MD5(CONCAT(country_iso3, '#', CAST(year AS STRING)))) AS country_year_key,
  CURRENT_TIMESTAMP() AS created_at,
  CURRENT_TIMESTAMP() AS updated_at
FROM spine
WHERE is_valid_entity_year = TRUE