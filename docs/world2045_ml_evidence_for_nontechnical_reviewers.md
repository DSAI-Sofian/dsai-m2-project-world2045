# World2045 ML Evidence for Non-Technical Reviewers

## What Was Actually Trained

We trained standard tabular ML models (not LLMs) on country-year indicator
history to forecast structural-risk indicators.

Models compared:

- carry-forward baseline (existing method)
- linear regression
- ridge regression
- random forest

Important: no foundation model fine-tuning was performed.

## What “Training and Testing” Means Here

Instead of training once and testing once, we used rolling-origin validation:

- train on earlier years
- test on later unseen years
- repeat this across multiple time windows

This better reflects real forecasting conditions.

## How Accuracy Was Measured

Primary metric: **MAE** (Mean Absolute Error).

Simple meaning:

- MAE is the average size of forecast error.
- Lower MAE means better accuracy.

## What Was Selected and Why

Final integration decisions:

- `climate_vulnerability`: **integrate** (ML showed stable improvement)
- `adaptation_readiness`: **defer** (improvement too small)
- `vdem_liberal_democracy_index`: **keep carry-forward** (ML underperformed)
- `conflict_severity`: **defer** (not integrated in this cycle)

## What Changed in the Dashboard

The dashboard now shows both forecast scenarios:

- `baseline_static_risk` (default)
- `baseline_ml_dynamic_risk`

Only climate vulnerability changes between the two scenarios. Governance,
adaptation, and conflict remain carry-forward in both.

## How to Read Scenario Delta Results

- Positive score delta: ML scenario score is higher than static baseline.
- Negative score delta: ML scenario score is lower than static baseline.
- Rank movement can appear larger than score movement because many countries
  are close together.

## Why This Is a Comparative Scenario

The ML scenario is designed for comparison and sensitivity analysis, not as a
single definitive forecast. The static baseline remains the reference anchor.
