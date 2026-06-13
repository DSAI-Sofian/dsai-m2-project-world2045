-- World2045 Streamlit export queries
-- Recommended execution target: small presentation-ready extracts.
-- Preferred storage format: parquet if you export via Python; CSV is acceptable for very small files.

-- 1) Global yearly trend
SELECT
  year,
  global_trajectory_score AS trajectory_score,
  scenario_id,
  is_forecast_year
FROM `{{ project }}.{{ dataset }}.gold__trajectory_global_year`
ORDER BY year;

-- 2) Regional yearly trend
SELECT
  region_name,
  year,
  avg_trajectory_score AS trajectory_score,
  scenario_id,
  is_forecast_year
FROM `{{ project }}.{{ dataset }}.gold__region_trajectory_score_year`
ORDER BY region_name, year;

-- 3) Country scenario score path
SELECT
  country_iso3,
  country_name,
  region_name,
  year,
  scenario_id,
  trajectory_score,
  is_forecast_year,
  forecast_score_completeness,
  assumption_flag,
  region,
  subregion,
  income_group,
  is_sovereign,
  climate_vulnerability_projection_source,
  climate_vulnerability_forecast_method
FROM `{{ project }}.{{ dataset }}.gold__country_trajectory_score_year_scenario`
WHERE scenario_id IN ('historical_observed', 'baseline_static_risk', 'baseline_ml_dynamic_risk')
ORDER BY country_name, year;

-- 4) Country component breakdown
SELECT
  country_iso3,
  country_name,
  year,
  component,
  component_score
FROM `{{ project }}.{{ dataset }}.gold__trajectory_component_breakdown`
ORDER BY country_name, year, component;

-- 5) Quadrant counts for overview
SELECT
  quadrant,
  COUNT(DISTINCT country_name) AS country_count
FROM `{{ project }}.{{ dataset }}.gold__trajectory_country_quadrant`
WHERE is_rankable_forecast_case = TRUE
  AND is_sovereign = TRUE
GROUP BY quadrant
ORDER BY country_count DESC;

-- 6) Strategic rankings table
SELECT
  rp.country_iso3,
  rp.country_name,
  rp.region_name,
  rp.trajectory_score_2023,
  rp.trajectory_score_2045,
  rp.trajectory_change_2023_2045,
  rp.rise_potential_score,
  m.momentum_score,
  q.quadrant,
  rp.is_rankable_forecast_case,
  rp.is_sovereign
FROM `{{ project }}.{{ dataset }}.gold__country_rise_potential` rp
LEFT JOIN `{{ project }}.{{ dataset }}.gold__country_trajectory_momentum` m
  USING (country_iso3, country_name, region_name)
LEFT JOIN `{{ project }}.{{ dataset }}.gold__trajectory_country_quadrant` q
  USING (country_iso3, country_name, region_name)
ORDER BY rise_potential_score DESC;

-- 7) Doomsday Clock input table
-- Create manually if you prefer, since this is a symbolic framing module.
-- Suggested schema:
--   snapshot_label STRING,
--   seconds_to_midnight FLOAT64,
--   risk_factor STRING,
--   risk_score FLOAT64

-- 8) Scenario delta summary (optional but recommended for Sprint 4 comparison section)
SELECT
  scope_type,
  scope_name,
  country_count,
  avg_score_delta,
  min_score_delta,
  max_score_delta,
  avg_rank_delta
FROM `{{ project }}.{{ dataset }}.gold__scenario_delta_summary`
ORDER BY scope_type, scope_name;

-- 9) Scenario delta country 2045 (optional but recommended for Sprint 4 comparison section)
SELECT
  country_iso3,
  country_name,
  region,
  subregion,
  income_group,
  is_sovereign,
  trajectory_score_static_2045,
  trajectory_score_ml_2045,
  trajectory_score_delta_ml_minus_static,
  trajectory_rank_static_2045,
  trajectory_rank_ml_2045,
  trajectory_rank_delta_static_minus_ml
FROM `{{ project }}.{{ dataset }}.gold__scenario_delta_country_2045`
ORDER BY ABS(trajectory_score_delta_ml_minus_static) DESC, country_iso3;
