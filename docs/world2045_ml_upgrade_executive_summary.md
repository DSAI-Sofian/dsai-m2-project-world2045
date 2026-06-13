# World2045 ML Upgrade Executive Summary

## Purpose

The World2045 ML upgrade adds a controlled machine-learning enhancement to the
forward scenario framework while preserving the original formula-based baseline.
The goal is better forward-looking climate-risk realism without destabilizing
the existing scoring system.

## What Changed

- Added a formal ML projection data contract (Sprint 1).
- Built and validated a structural-risk ML pipeline (Sprints 2/2B).
- Integrated ML only for `climate_vulnerability` into a new scenario
  `baseline_ml_dynamic_risk` (Sprint 3).
- Preserved existing `baseline_static_risk` behavior and parity.
- Exposed both scenarios in the dashboard with comparison views (Sprints 4/4B).

## Scenario Structure for Stakeholders

- `historical_observed`:
  - actual historical values, used for historical interpretation only.
- `baseline_static_risk` (default):
  - projected macro variables with carry-forward structural risk assumptions.
- `baseline_ml_dynamic_risk`:
  - same as static baseline except climate vulnerability uses validated ML
    projection where available, with carry-forward fallback.

## Key Business Message

The ML scenario is a comparative decision-support lens, not a replacement for
the static baseline. It helps identify where dynamic climate-risk assumptions
could materially affect country trajectories and rankings.

## Why Only Climate Was Integrated

- Climate vulnerability showed the strongest validation case among tested
  structural-risk indicators.
- Governance and adaptation readiness did not consistently outperform
  carry-forward in validation.
- Conflict forecasting was deferred due higher volatility, data constraints,
  and risk of unstable projections.

## Governance and Risk Controls

- Static baseline parity preserved and tested.
- Explicit fallback logic for climate ML projections.
- Scenario coverage parity checks between static and ML scenarios.
- Projection-source and forecast-method metadata exposed for transparency.

## Current Limitations

- Only climate vulnerability is ML-integrated.
- ML coverage can be partial for some country-year combinations.
- Conflict remains carry-forward pending a stronger forecasting approach.
- ML scenario outputs should be interpreted as comparative, not definitive.

## Recommended Next Steps

1. Expand governance/adaptation experimentation only if new evidence beats
   carry-forward robustly.
2. Design a dedicated conflict-forecast track with uncertainty-aware methods.
3. Add periodic model monitoring and versioned refresh cadence.
4. Formalize sign-off gates for moving additional indicators into production.
