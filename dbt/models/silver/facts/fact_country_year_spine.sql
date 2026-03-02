{{ config(materialized="table") }}

-- Canonical country-year spine
-- Grain: (country_iso3, year)
-- All domain facts must LEFT JOIN to this spine.

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
      WHEN c.valid_to_year IS NOT NULL AND y.year > c.valid_to_year THEN FALSE
      ELSE TRUE
    END AS is_valid_entity_year
  FROM countries c
  CROSS JOIN years y
)

SELECT
  country_iso3,
  year,
  TRUE AS is_valid_entity_year,  -- rows filtered to valid only
  TO_HEX(MD5(CONCAT(country_iso3, '#', CAST(year AS STRING)))) AS country_year_key,
  CURRENT_TIMESTAMP() AS created_at,
  CURRENT_TIMESTAMP() AS updated_at
FROM spine
WHERE is_valid_entity_year