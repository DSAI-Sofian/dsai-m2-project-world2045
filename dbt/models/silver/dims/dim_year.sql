{{ config(materialized="table") }}

-- Canonical year dimension.
-- Year range controlled by vars:
--   year_start (default 1945)
--   year_end   (default 2100)

{% set year_start = var('year_start', 1945) %}
{% set year_end   = var('year_end', 2100) %}

WITH years AS (
  SELECT year
  FROM UNNEST(GENERATE_ARRAY({{ year_start }}, {{ year_end }})) AS year
)

SELECT
  year,
  CAST(FLOOR(year / 10) * 10 AS INT64) AS decade,
  year >= 1945 AS post_ww2_flag,
  CURRENT_TIMESTAMP() AS created_at,
  CURRENT_TIMESTAMP() AS updated_at
FROM years