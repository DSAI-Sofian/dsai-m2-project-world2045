# World2045 ML Upgrade Audit Checklist

Use this checklist for release review, governance sign-off, and client handoff.

## A) Scenario Integrity

- [ ] `historical_observed` clearly separated from forecast scenarios.
- [ ] `baseline_static_risk` remains default in dashboard.
- [ ] `baseline_static_risk` logic unchanged from approved baseline.
- [ ] `baseline_ml_dynamic_risk` exists and is selectable.
- [ ] ML integration is climate-only in current release.

## B) Indicator-Level Rules

- [ ] `climate_vulnerability` uses ML projection with explicit fallback.
- [ ] `vdem_liberal_democracy_index` remains carry-forward.
- [ ] `adaptation_readiness` remains carry-forward.
- [ ] `conflict_severity` remains carry-forward/deferred.

## C) Data Contract and Metadata

- [ ] Projection contract fields are present and populated for integrated rows.
- [ ] `climate_vulnerability_projection_source` available downstream.
- [ ] `climate_vulnerability_forecast_method` available downstream.
- [ ] Scenario coverage parity checks pass for forecast years.

## D) Validation Evidence

- [ ] Rolling-origin validation evidence archived.
- [ ] Model selection decisions archived by indicator.
- [ ] Regional diagnostics archived where available.
- [ ] Forecast sanity checks archived.

## E) Dashboard Readiness

- [ ] Dashboard exports refreshed after latest dbt run.
- [ ] Both forecast scenarios visible in selector.
- [ ] Scenario comparison section is populated.
- [ ] Missing comparison files fail gracefully (no crash).
- [ ] Methodology text explains scenario differences.

## F) Documentation Completeness

- [ ] Executive summary current.
- [ ] Technical completion report current.
- [ ] Demo walkthrough current.
- [ ] Model card current.
- [ ] Forecasting methodology current.
- [ ] Changelog updated with latest sprint.

## G) Risk and Governance

- [ ] Documentation states ML scenario is comparative, not definitive.
- [ ] Limitations are explicit (coverage, deferred indicators, uncertainty).
- [ ] Future work plan defined before expanding ML integration scope.
