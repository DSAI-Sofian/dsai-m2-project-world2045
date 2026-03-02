{{ config(materialized="table") }}

-- dim_country built from seed: seeds/country_overrides.csv
-- Canonical key: ISO-3166-1 alpha-3 (country_iso3)

WITH src AS (
  SELECT
    {{ norm_iso3("iso3") }} AS country_iso3,
    TRIM(country_name) AS country_name,

    NULLIF(TRIM(CAST(country_name_official AS STRING)), "") AS country_name_official,
    NULLIF(TRIM(CAST(iso2 AS STRING)), "") AS country_iso2,
    NULLIF(TRIM(CAST(iso_numeric AS STRING)), "") AS country_numeric,
    NULLIF(TRIM(CAST(region AS STRING)), "") AS region,
    NULLIF(TRIM(CAST(subregion AS STRING)), "") AS subregion,
    NULLIF(TRIM(CAST(income_group AS STRING)), "") AS income_group,

    SAFE_CAST(is_sovereign AS BOOL) AS is_sovereign,
    SAFE_CAST(is_disputed AS BOOL) AS is_disputed,

    {{ safe_int("valid_from_year") }} AS valid_from_year,
    {{ safe_int("valid_to_year") }} AS valid_to_year,

    NULLIF({{ norm_iso3("predecessor_iso3") }}, "") AS predecessor_iso3,
    NULLIF({{ norm_iso3("successor_iso3") }}, "") AS successor_iso3

  FROM {{ ref('country_overrides') }}
)

SELECT
  country_iso3,
  country_name,
  country_name_official,
  country_iso2,
  country_numeric,
  region,
  subregion,
  income_group,
  is_sovereign,
  is_disputed,
  valid_from_year,
  valid_to_year,
  predecessor_iso3,
  successor_iso3,
  CURRENT_TIMESTAMP() AS created_at,
  CURRENT_TIMESTAMP() AS updated_at
FROM src
WHERE country_iso3 IS NOT NULL