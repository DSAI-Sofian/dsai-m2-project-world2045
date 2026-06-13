# ML Forecasting Methodology (World2045)

## Scope

This document defines the forecasting approach used in the ML upgrade and the
current production integration boundary.

## Indicator Coverage and Decisions

- `climate_vulnerability`: integrated into `baseline_ml_dynamic_risk`
- `adaptation_readiness`: keep carry-forward (not integrated)
- `vdem_liberal_democracy_index`: keep carry-forward (not integrated)
- `conflict_severity`: deferred (not integrated)

## Why Only Climate Is Integrated

- Validation indicated the most supportable uplift relative to carry-forward.
- Governance and adaptation results were not consistently superior.
- Conflict dynamics are higher volatility and require a separate method track.

## Modeling Pipeline Summary

## 1) Panel construction

- Build country-year indicator panel for modelable indicators.
- Use lag/rolling/change features and missingness flags.

## 2) Baseline and candidate models

- Baseline: carry-forward
- Candidates:
  - linear regression
  - ridge regression
  - random forest (when available)

## 3) Validation design

- Rolling-origin folds:
  - train to 2005, test 2006-2010
  - train to 2010, test 2011-2015
  - train to 2015, test 2016-2020
  - train to 2020, test 2021-2023
- Regional diagnostics where coverage permits.
- Sanity checks:
  - valid ranges
  - jump limits
  - null prevention
  - fallback when unstable/weaker

## 4) Output contract

Forecast records use the structural-risk projection contract:

- `country_iso3`
- `year`
- `scenario_id`
- `indicator_name`
- `projected_value`
- `projection_source`
- `forecast_method`
- `model_version`
- `created_at`

## Integration Methodology

Integration is scenario-gated:

- `baseline_static_risk`: formula/carry-forward baseline unchanged.
- `baseline_ml_dynamic_risk`: climate vulnerability uses ML projection where
  available, otherwise carry-forward fallback.

This preserves continuity while enabling comparative ML analysis.

## Interpretation Guidance

- Treat ML scenario as comparative, not definitive.
- Always compare against static baseline before drawing conclusions.
- Use delta outputs (`gold__scenario_delta_*`) to identify meaningful changes.

## Future Methodology Enhancements

1. Add uncertainty bands and confidence diagnostics per country-year.
2. Introduce model monitoring drift checks per refresh cycle.
3. Pilot hybrid conflict models before considering integration.
4. Reassess governance/adaptation only after stronger out-of-sample evidence.
