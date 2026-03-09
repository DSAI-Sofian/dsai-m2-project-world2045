# dbt Model Pattern

All domain facts follow this pattern.

1.  Use country‑year spine
2.  Pull indicators from silver\_\_wdi_country_year_long
3.  Aggregate to country_iso3 + year
4.  Join back to spine

Example structure:

WITH spine AS ( SELECT country_iso3, year FROM fact_country_year_spine )

indicator AS ( SELECT country_iso3, year, value FROM
silver\_\_wdi_country_year_long )

SELECT s.country_iso3, s.year, i.value FROM spine s LEFT JOIN indicator
i ON s.country_iso3 = i.country_iso3 AND s.year = i.year
