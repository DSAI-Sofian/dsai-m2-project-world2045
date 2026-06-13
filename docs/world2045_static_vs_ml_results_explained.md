# World2045 Static vs ML Results Explained

## Plain-Language Difference

## Static baseline (`baseline_static_risk`)

- Uses carry-forward assumptions for governance, adaptation readiness, climate
  vulnerability, and conflict.
- This is the continuity baseline and remains the default dashboard view.

## ML dynamic risk (`baseline_ml_dynamic_risk`)

- Same structure as static baseline except climate vulnerability uses validated
  ML projection where available.
- Uses fallback to carry-forward climate values when ML coverage is not
  available.

## What Changes Numerically

- Most forecast mechanics remain the same.
- The main source of difference is climate vulnerability treatment.
- As a result, score differences can be modest while rank shifts can still be
  noticeable in tightly clustered country groups.

## Reading the Delta Tables

From `scenario_delta_summary` and `scenario_delta_country_2045`:

- `trajectory_score_delta_ml_minus_static > 0`:
  - ML dynamic scenario score is higher than static baseline.
- `trajectory_score_delta_ml_minus_static < 0`:
  - ML dynamic scenario score is lower than static baseline.
- `trajectory_rank_delta_static_minus_ml`:
  - positive means rank improved under ML dynamic scenario
  - negative means rank worsened under ML dynamic scenario

## Why Only Climate Was Integrated

- Climate vulnerability had the strongest validated performance signal.
- Governance and adaptation did not show consistent practical gains.
- Conflict forecasting was deferred to avoid unstable integration.

## What Did Not Change

- Historical observed data remains unchanged.
- Static baseline logic remains parity-preserved.
- No ML training logic, scoring SQL logic, or seed logic changed in this
  comparison step.

## Recommended Interpretation

- Use static baseline for continuity and anchor decisions.
- Use ML dynamic risk as a sensitivity/comparison layer.
- Do not interpret ML dynamic risk as a final definitive forecast.
