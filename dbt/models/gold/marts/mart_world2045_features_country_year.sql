{{ config(materialized="table") }}

-- Phase 0 placeholder: select from spine.
-- Later, this will select from fact_country_year_core / feature tables.

SELECT
  country_iso3,
  year
FROM {{ ref('fact_country_year_spine') }}
WHERE year <= 2045