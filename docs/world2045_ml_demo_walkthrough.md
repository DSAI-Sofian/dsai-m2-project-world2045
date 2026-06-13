# World2045 ML Demo Walkthrough

## Audience

Non-technical reviewers, management, and client stakeholders.

## Demo Objective

Show how the ML-enhanced comparative scenario changes interpretation versus the
static baseline, while keeping the original baseline intact.

## Pre-Demo Checklist

1. Ensure dashboard exports are refreshed in `dashboard/data/`.
2. Confirm both scenarios are available in forecast views:
   - `baseline_static_risk`
   - `baseline_ml_dynamic_risk`
3. Confirm comparison files exist:
   - `scenario_delta_summary.csv`
   - `scenario_delta_country_2045.csv`

## Run the Dashboard

From repository root:

```bash
cd dashboard
streamlit run app/app.py
```

## Suggested 10-Minute Script

## 1) Set framing (1 minute)

- Explain that the dashboard now supports:
  - historical observed results
  - static baseline forecast
  - ML dynamic risk comparative forecast
- Clarify that static baseline remains default.

## 2) Global Overview (3 minutes)

- Keep scenario on `baseline_static_risk` first.
- Highlight global trend and explain it represents the baseline assumption set.
- Switch to `baseline_ml_dynamic_risk`.
- Show the scenario comparison section:
  - summary deltas (global/region)
  - most affected countries by 2045 score delta

## 3) Country Explorer (3 minutes)

- Pick a country with visible delta impact.
- Compare trajectory path under static vs ML dynamic scenario.
- Show climate projection metadata fields where available:
  - projection source
  - forecast method
- Explain fallback behavior when ML projection is unavailable.

## 4) Regional View (2 minutes)

- Compare one region under both scenarios.
- Emphasize that differences stem from climate vulnerability treatment only.

## 5) Methodology page closeout (1 minute)

- Reiterate:
  - governance/adaptation/conflict remain carry-forward
  - ML scenario is comparative, not definitive

## Recommended Talking Points

- We preserved baseline continuity and added a controlled ML comparison lane.
- We integrated only where validation support was strongest (climate).
- We intentionally deferred weaker/unstable ML candidates.
- The product now improves transparency via scenario metadata and delta views.

## FAQ Prompts for Reviewers

- Why is static baseline still default?
  - It is parity-stable and acts as the policy/operational anchor.
- Is ML now “the truth” scenario?
  - No. It is a validated comparative scenario for sensitivity analysis.
- Why not include conflict ML now?
  - Current evidence and data volatility do not yet support robust integration.

## Demo Exit Criteria

- Reviewer can explain difference between static and ML dynamic scenarios.
- Reviewer can locate scenario delta outputs.
- Reviewer understands ML scope is currently climate-only.
