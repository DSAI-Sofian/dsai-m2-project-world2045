#!/usr/bin/env python3
"""Train and backtest Sprint 2B structural-risk forecast models.

Outputs:
- ML-ready panel dataset (observed years)
- Rolling-origin validation metrics and comparisons
- Regional metrics (if region data is available)
- Coverage + sanity checks
- Forecast artifact in Sprint 1 contract format for 2024-2045
"""

from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Callable

import numpy as np
import pandas as pd

INDICATORS = (
    "vdem_liberal_democracy_index",
    "adaptation_readiness",
    "climate_vulnerability",
)

FEATURE_COLUMNS = (
    "prev_year_value",
    "rolling_mean_3y",
    "rolling_mean_5y",
    "change_3y",
    "change_5y",
    "is_prev_year_missing",
    "is_rolling_mean_3y_missing",
    "is_rolling_mean_5y_missing",
)

FORECAST_START_YEAR = 2024
FORECAST_END_YEAR = 2045
PANEL_START_YEAR = 1995
PANEL_END_YEAR = 2023

ROLLING_ORIGIN_FOLDS = (
    ("train_to_2005_test_2006_2010", 2005, 2006, 2010),
    ("train_to_2010_test_2011_2015", 2010, 2011, 2015),
    ("train_to_2015_test_2016_2020", 2015, 2016, 2020),
    ("train_to_2020_test_2021_2023", 2020, 2021, 2023),
)

HARD_BOUNDS = {
    "vdem_liberal_democracy_index": (0.0, 1.0),
    "adaptation_readiness": (0.0, 1.0),
    "climate_vulnerability": (0.0, 1.0),
}


@dataclass
class ModelBundle:
    name: str
    fit_fn: Callable[[pd.DataFrame, pd.Series], object]
    predict_fn: Callable[[object, pd.DataFrame], np.ndarray]


def metric_mae(actual: np.ndarray, pred: np.ndarray) -> float:
    return float(np.mean(np.abs(actual - pred)))


def metric_rmse(actual: np.ndarray, pred: np.ndarray) -> float:
    return float(np.sqrt(np.mean((actual - pred) ** 2)))


def metric_smape(actual: np.ndarray, pred: np.ndarray) -> float:
    denom = np.abs(actual) + np.abs(pred)
    safe = np.where(denom == 0, 1.0, denom)
    return float(np.mean(2.0 * np.abs(pred - actual) / safe))


def fit_linear_numpy(x: pd.DataFrame, y: pd.Series) -> dict[str, np.ndarray]:
    x_arr = x.to_numpy(dtype=float)
    y_arr = y.to_numpy(dtype=float)
    x_aug = np.c_[np.ones(len(x_arr)), x_arr]
    beta, *_ = np.linalg.lstsq(x_aug, y_arr, rcond=None)
    return {"coef": beta}


def predict_linear_numpy(model: dict[str, np.ndarray], x: pd.DataFrame) -> np.ndarray:
    x_arr = x.to_numpy(dtype=float)
    x_aug = np.c_[np.ones(len(x_arr)), x_arr]
    return x_aug @ model["coef"]


def fit_ridge_numpy(alpha: float) -> Callable[[pd.DataFrame, pd.Series], dict[str, np.ndarray]]:
    def _fit(x: pd.DataFrame, y: pd.Series) -> dict[str, np.ndarray]:
        x_arr = x.to_numpy(dtype=float)
        y_arr = y.to_numpy(dtype=float)
        x_aug = np.c_[np.ones(len(x_arr)), x_arr]
        eye = np.eye(x_aug.shape[1])
        eye[0, 0] = 0.0
        beta = np.linalg.solve(x_aug.T @ x_aug + alpha * eye, x_aug.T @ y_arr)
        return {"coef": beta}

    return _fit


def predict_ridge_numpy(model: dict[str, np.ndarray], x: pd.DataFrame) -> np.ndarray:
    return predict_linear_numpy(model, x)


def try_load_sklearn_models() -> list[ModelBundle]:
    bundles: list[ModelBundle] = []
    try:
        from sklearn.ensemble import RandomForestRegressor
        from sklearn.linear_model import LinearRegression, Ridge
    except ImportError:
        return bundles

    bundles.append(
        ModelBundle(
            name="linear_regression_sklearn",
            fit_fn=lambda x, y: LinearRegression().fit(x, y),
            predict_fn=lambda model, x: model.predict(x),
        )
    )
    bundles.append(
        ModelBundle(
            name="ridge_regression_sklearn",
            fit_fn=lambda x, y: Ridge(alpha=1.0, random_state=42).fit(x, y),
            predict_fn=lambda model, x: model.predict(x),
        )
    )
    bundles.append(
        ModelBundle(
            name="random_forest_sklearn",
            fit_fn=lambda x, y: RandomForestRegressor(
                n_estimators=30,
                max_depth=8,
                min_samples_leaf=2,
                random_state=42,
                n_jobs=1,
            ).fit(x, y),
            predict_fn=lambda model, x: model.predict(x),
        )
    )
    return bundles


def base_model_bundles() -> list[ModelBundle]:
    sklearn_bundles = try_load_sklearn_models()
    if sklearn_bundles:
        return sklearn_bundles

    return [
        ModelBundle(
            name="linear_regression_numpy",
            fit_fn=fit_linear_numpy,
            predict_fn=predict_linear_numpy,
        ),
        ModelBundle(
            name="ridge_regression_numpy",
            fit_fn=fit_ridge_numpy(alpha=1.0),
            predict_fn=predict_ridge_numpy,
        ),
    ]


def load_region_map(repo_root: Path) -> pd.DataFrame:
    seed_path = repo_root / "dbt" / "seeds" / "country_overrides.csv"
    if not seed_path.exists():
        return pd.DataFrame(columns=["country_iso3", "region", "subregion"])

    df = pd.read_csv(seed_path, usecols=["iso3", "region", "subregion"])
    df = df.rename(columns={"iso3": "country_iso3"})
    df["country_iso3"] = df["country_iso3"].astype(str).str.upper().str.strip()
    return df


def load_indicator_sources(data_root: Path) -> pd.DataFrame:
    vdem_path = data_root / "raw" / "vdem" / "vdem_country_year.csv"
    nd_gain_path = data_root / "bronze" / "nd_gain_country_year.parquet"

    if not vdem_path.exists():
        raise FileNotFoundError(f"Missing governance source file: {vdem_path}")
    if not nd_gain_path.exists():
        raise FileNotFoundError(f"Missing climate source file: {nd_gain_path}")

    vdem = pd.read_csv(
        vdem_path,
        usecols=["country_iso3", "year", "vdem_liberal_democracy_index"],
    )
    climate = pd.read_parquet(
        nd_gain_path,
        columns=["country_iso3", "year", "adaptation_readiness", "climate_vulnerability"],
    )

    merged = vdem.merge(climate, on=["country_iso3", "year"], how="outer").copy()
    merged["country_iso3"] = merged["country_iso3"].astype(str).str.upper().str.strip()
    merged["year"] = pd.to_numeric(merged["year"], errors="coerce").astype("Int64")

    for col in INDICATORS:
        merged[col] = pd.to_numeric(merged[col], errors="coerce")

    merged = merged[
        merged["country_iso3"].str.len().eq(3)
        & merged["year"].between(PANEL_START_YEAR, PANEL_END_YEAR)
    ].copy()

    return merged


def build_ml_panel(indicator_wide: pd.DataFrame, region_map: pd.DataFrame) -> pd.DataFrame:
    countries = sorted(indicator_wide["country_iso3"].dropna().unique().tolist())
    years = list(range(PANEL_START_YEAR, PANEL_END_YEAR + 1))

    spine = pd.MultiIndex.from_product(
        [countries, years],
        names=["country_iso3", "year"],
    ).to_frame(index=False)

    panel = spine.merge(indicator_wide, on=["country_iso3", "year"], how="left")
    panel = panel.merge(region_map, on="country_iso3", how="left")

    long = panel.melt(
        id_vars=["country_iso3", "year", "region", "subregion"],
        value_vars=list(INDICATORS),
        var_name="indicator_name",
        value_name="indicator_value",
    ).sort_values(["indicator_name", "country_iso3", "year"])

    long["prev_year_value"] = (
        long.groupby(["country_iso3", "indicator_name"])["indicator_value"].shift(1)
    )
    long["rolling_mean_3y"] = long.groupby(
        ["country_iso3", "indicator_name"]
    )["indicator_value"].transform(lambda s: s.shift(1).rolling(3, min_periods=1).mean())
    long["rolling_mean_5y"] = long.groupby(
        ["country_iso3", "indicator_name"]
    )["indicator_value"].transform(lambda s: s.shift(1).rolling(5, min_periods=1).mean())

    lag_1 = long.groupby(["country_iso3", "indicator_name"])["indicator_value"].shift(1)
    lag_4 = long.groupby(["country_iso3", "indicator_name"])["indicator_value"].shift(4)
    lag_6 = long.groupby(["country_iso3", "indicator_name"])["indicator_value"].shift(6)
    long["change_3y"] = lag_1 - lag_4
    long["change_5y"] = lag_1 - lag_6

    long["is_indicator_missing"] = long["indicator_value"].isna().astype(int)
    long["is_prev_year_missing"] = long["prev_year_value"].isna().astype(int)
    long["is_rolling_mean_3y_missing"] = long["rolling_mean_3y"].isna().astype(int)
    long["is_rolling_mean_5y_missing"] = long["rolling_mean_5y"].isna().astype(int)

    return long.reset_index(drop=True)


def impute_features(train_x: pd.DataFrame, test_x: pd.DataFrame, fallback: float) -> tuple[pd.DataFrame, pd.DataFrame, pd.Series]:
    medians = train_x.median(numeric_only=True).fillna(fallback)
    return train_x.fillna(medians), test_x.fillna(medians), medians


def build_feature_row(series: pd.DataFrame, year: int) -> tuple[pd.DataFrame, float]:
    prev = series.loc[series["year"] == year - 1, "indicator_value"]
    prev_value = float(prev.iloc[0]) if not prev.empty else np.nan

    prior = series[series["year"] < year].sort_values("year")
    roll3 = float(prior["indicator_value"].tail(3).mean()) if not prior.empty else np.nan
    roll5 = float(prior["indicator_value"].tail(5).mean()) if not prior.empty else np.nan

    lag4 = series.loc[series["year"] == year - 4, "indicator_value"]
    lag6 = series.loc[series["year"] == year - 6, "indicator_value"]
    chg3 = prev_value - float(lag4.iloc[0]) if not lag4.empty and pd.notna(prev_value) else np.nan
    chg5 = prev_value - float(lag6.iloc[0]) if not lag6.empty and pd.notna(prev_value) else np.nan

    feat = pd.DataFrame([
        {
            "prev_year_value": prev_value,
            "rolling_mean_3y": roll3,
            "rolling_mean_5y": roll5,
            "change_3y": chg3,
            "change_5y": chg5,
            "is_prev_year_missing": int(pd.isna(prev_value)),
            "is_rolling_mean_3y_missing": int(pd.isna(roll3)),
            "is_rolling_mean_5y_missing": int(pd.isna(roll5)),
        }
    ])

    fallback = (
        prev_value
        if pd.notna(prev_value)
        else float(series["indicator_value"].dropna().tail(1).iloc[0])
    )
    return feat, fallback


def forecast_one_series(
    history: pd.DataFrame,
    years: list[int],
    model_name: str,
    fitted_model: tuple[ModelBundle, object] | None,
    feature_medians: pd.Series,
) -> pd.DataFrame:
    series = history.sort_values("year")[["year", "indicator_value"]].copy()
    out_rows: list[dict] = []

    for year in years:
        feat, fallback = build_feature_row(series, year)

        if model_name == "carry_forward_baseline" or fitted_model is None:
            pred = fallback
        else:
            bundle, model_obj = fitted_model
            feat_filled = feat.fillna(feature_medians).fillna(fallback)
            try:
                pred = float(bundle.predict_fn(model_obj, feat_filled)[0])
            except Exception:
                pred = fallback

        series = pd.concat(
            [series, pd.DataFrame([{"year": year, "indicator_value": pred}])],
            ignore_index=True,
        )
        out_rows.append({"year": year, "predicted": pred})

    return pd.DataFrame(out_rows)


def fit_model_for_indicator(
    train_df: pd.DataFrame,
    model_name: str,
    bundles: list[ModelBundle],
) -> tuple[tuple[ModelBundle, object] | None, pd.Series]:
    if model_name == "carry_forward_baseline":
        return None, pd.Series(dtype=float)

    bundle = next((m for m in bundles if m.name == model_name), None)
    if bundle is None:
        return None, pd.Series(dtype=float)

    x = train_df[list(FEATURE_COLUMNS)].copy()
    y = train_df["indicator_value"].copy()
    fallback = float(y.median()) if y.notna().any() else 0.0
    x_train, _, medians = impute_features(x, x.copy(), fallback)

    model = bundle.fit_fn(x_train, y)
    return (bundle, model), medians


def rolling_origin_predictions(panel: pd.DataFrame, bundles: list[ModelBundle]) -> pd.DataFrame:
    model_names = ["carry_forward_baseline", *[m.name for m in bundles]]
    rows: list[dict] = []

    for indicator in INDICATORS:
        idf = panel[panel["indicator_name"] == indicator].copy().sort_values(["country_iso3", "year"])

        for fold_name, train_end, test_start, test_end in ROLLING_ORIGIN_FOLDS:
            train = idf[(idf["year"] <= train_end) & idf["indicator_value"].notna()].copy()
            if train.empty:
                continue

            for model_name in model_names:
                fitted, medians = fit_model_for_indicator(train, model_name, bundles)

                for iso3, cdf in idf.groupby("country_iso3", sort=True):
                    history = cdf[(cdf["year"] <= train_end) & cdf["indicator_value"].notna()][["year", "indicator_value"]].copy()
                    if history.empty:
                        continue

                    preds = forecast_one_series(
                        history=history,
                        years=list(range(test_start, test_end + 1)),
                        model_name=model_name,
                        fitted_model=fitted,
                        feature_medians=medians,
                    )

                    truth = cdf[(cdf["year"] >= test_start) & (cdf["year"] <= test_end) & cdf["indicator_value"].notna()][
                        ["year", "indicator_value", "region", "subregion"]
                    ].copy()
                    if truth.empty:
                        continue

                    merged = truth.merge(preds, on="year", how="left")
                    merged = merged[merged["predicted"].notna()].copy()
                    if merged.empty:
                        continue

                    for _, row in merged.iterrows():
                        rows.append(
                            {
                                "indicator_name": indicator,
                                "fold": fold_name,
                                "train_end_year": train_end,
                                "test_start_year": test_start,
                                "test_end_year": test_end,
                                "model_name": model_name,
                                "country_iso3": iso3,
                                "region": row.get("region"),
                                "subregion": row.get("subregion"),
                                "year": int(row["year"]),
                                "actual": float(row["indicator_value"]),
                                "predicted": float(row["predicted"]),
                                "abs_error": float(abs(row["predicted"] - row["indicator_value"])),
                            }
                        )

    return pd.DataFrame(rows)


def summarize_predictions(pred_df: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    if pred_df.empty:
        return pd.DataFrame(), pd.DataFrame()

    fold_metrics = (
        pred_df.groupby(["indicator_name", "model_name", "fold"], as_index=False)
        .agg(
            mae=("abs_error", "mean"),
            rmse=("abs_error", lambda s: float(np.sqrt(np.mean(np.square(s.to_numpy(dtype=float)))))),
            n_obs=("abs_error", "size"),
        )
        .sort_values(["indicator_name", "fold", "mae"])
    )

    summary = (
        pred_df.groupby(["indicator_name", "model_name"], as_index=False)
        .agg(
            mae=("abs_error", "mean"),
            rmse=("abs_error", lambda s: float(np.sqrt(np.mean(np.square(s.to_numpy(dtype=float)))))),
            n_obs=("abs_error", "size"),
            eval_years=("year", "nunique"),
            eval_folds=("fold", "nunique"),
        )
        .sort_values(["indicator_name", "mae"])
    )

    out = []
    for indicator in INDICATORS:
        local = summary[summary["indicator_name"] == indicator].copy()
        if local.empty:
            continue
        baseline = local[local["model_name"] == "carry_forward_baseline"]
        baseline_mae = float(baseline["mae"].iloc[0]) if not baseline.empty else np.nan
        local["beats_carry_forward"] = local["mae"] < baseline_mae
        local["mae_delta_vs_carry_forward"] = local["mae"] - baseline_mae
        out.append(local)

    return fold_metrics, pd.concat(out, ignore_index=True) if out else pd.DataFrame()


def regional_metrics(pred_df: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    if pred_df.empty or "region" not in pred_df.columns:
        return pd.DataFrame(), pd.DataFrame()

    reg = pred_df[pred_df["region"].notna()].copy()
    if reg.empty:
        return pd.DataFrame(), pd.DataFrame()

    metrics = (
        reg.groupby(["indicator_name", "region", "model_name"], as_index=False)
        .agg(mae=("abs_error", "mean"), n_obs=("abs_error", "size"))
        .sort_values(["indicator_name", "region", "mae"])
    )

    baseline = metrics[metrics["model_name"] == "carry_forward_baseline"][
        ["indicator_name", "region", "mae"]
    ].rename(columns={"mae": "baseline_mae"})

    comp = metrics.merge(baseline, on=["indicator_name", "region"], how="left")
    comp["mae_delta_vs_carry_forward"] = comp["mae"] - comp["baseline_mae"]
    worse = comp[(comp["model_name"] != "carry_forward_baseline") & (comp["mae_delta_vs_carry_forward"] > 0)].copy()

    return comp, worse


def selection_decisions(summary_metrics: pd.DataFrame, fold_metrics: pd.DataFrame) -> pd.DataFrame:
    rows: list[dict] = []

    for indicator in INDICATORS:
        local = summary_metrics[summary_metrics["indicator_name"] == indicator].copy()
        baseline = local[local["model_name"] == "carry_forward_baseline"]

        if local.empty or baseline.empty:
            rows.append(
                {
                    "indicator_name": indicator,
                    "selected_model": "carry_forward_baseline",
                    "decision": "keep carry-forward",
                    "reason": "no comparable baseline metrics",
                }
            )
            continue

        baseline_mae = float(baseline["mae"].iloc[0])
        ml_candidates = local[local["model_name"] != "carry_forward_baseline"].sort_values("mae")

        if ml_candidates.empty:
            rows.append(
                {
                    "indicator_name": indicator,
                    "selected_model": "carry_forward_baseline",
                    "decision": "keep carry-forward",
                    "reason": "no ML candidate metrics",
                }
            )
            continue

        best = ml_candidates.iloc[0]
        best_model = str(best["model_name"])
        best_mae = float(best["mae"])
        improvement = baseline_mae - best_mae
        rel_improvement = improvement / baseline_mae if baseline_mae > 0 else 0.0

        fold_local = fold_metrics[fold_metrics["indicator_name"] == indicator]
        fold_baseline = fold_local[fold_local["model_name"] == "carry_forward_baseline"][
            ["fold", "mae"]
        ].rename(columns={"mae": "baseline_mae"})
        fold_best = fold_local[fold_local["model_name"] == best_model][["fold", "mae"]].rename(
            columns={"mae": "best_mae"}
        )

        fold_compare = fold_best.merge(fold_baseline, on="fold", how="inner")
        fold_win_rate = (
            float((fold_compare["best_mae"] < fold_compare["baseline_mae"]).mean())
            if not fold_compare.empty
            else 0.0
        )

        if improvement <= 0:
            decision = "keep carry-forward"
            selected_model = "carry_forward_baseline"
            reason = "best ML does not beat carry-forward"
        elif rel_improvement < 0.005:
            decision = "defer"
            selected_model = "carry_forward_baseline"
            reason = "ML improvement is too small"
        elif fold_win_rate < 0.75:
            decision = "defer"
            selected_model = "carry_forward_baseline"
            reason = "ML is not stable across rolling-origin folds"
        else:
            decision = "integrate"
            selected_model = best_model
            reason = "ML beats carry-forward with stable rolling-origin performance"

        rows.append(
            {
                "indicator_name": indicator,
                "selected_model": selected_model,
                "best_ml_model": best_model,
                "decision": decision,
                "reason": reason,
                "baseline_mae": baseline_mae,
                "best_ml_mae": best_mae,
                "mae_improvement": improvement,
                "relative_improvement": rel_improvement,
                "fold_win_rate": fold_win_rate,
            }
        )

    return pd.DataFrame(rows).sort_values("indicator_name")


def derive_sanity_thresholds(panel: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for indicator in INDICATORS:
        idf = panel[(panel["indicator_name"] == indicator) & panel["indicator_value"].notna()].copy()
        if idf.empty:
            rows.append(
                {
                    "indicator_name": indicator,
                    "lower_bound": HARD_BOUNDS[indicator][0],
                    "upper_bound": HARD_BOUNDS[indicator][1],
                    "max_yoy_jump": 0.05,
                }
            )
            continue

        low, high = HARD_BOUNDS.get(indicator, (float(idf["indicator_value"].min()), float(idf["indicator_value"].max())))

        diffs = (
            idf.sort_values(["country_iso3", "year"]) 
            .groupby("country_iso3")["indicator_value"]
            .diff()
            .abs()
            .dropna()
        )
        if diffs.empty:
            jump = 0.05
        else:
            jump = float(max(diffs.quantile(0.99), diffs.quantile(0.95) * 1.25, 0.02))

        rows.append(
            {
                "indicator_name": indicator,
                "lower_bound": float(low),
                "upper_bound": float(high),
                "max_yoy_jump": float(jump),
            }
        )

    return pd.DataFrame(rows)


def generate_forecasts(
    panel: pd.DataFrame,
    bundles: list[ModelBundle],
    decisions: pd.DataFrame,
    thresholds: pd.DataFrame,
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    now_utc = datetime.now(timezone.utc).isoformat()
    forecast_rows = []
    coverage_rows = []
    sanity_rows = []

    threshold_map = {
        r["indicator_name"]: r for _, r in thresholds.iterrows()
    }

    for indicator in INDICATORS:
        idf = panel[panel["indicator_name"] == indicator].copy().sort_values(["country_iso3", "year"])

        decision_row = decisions[decisions["indicator_name"] == indicator].iloc[0]
        model_name = str(decision_row["selected_model"])

        train = idf[idf["indicator_value"].notna()].copy()
        fitted, medians = fit_model_for_indicator(train, model_name, bundles)

        threshold = threshold_map[indicator]
        lower_bound = float(threshold["lower_bound"])
        upper_bound = float(threshold["upper_bound"])
        max_jump = float(threshold["max_yoy_jump"])

        eligible = 0
        null_fallback_count = 0
        jump_fallback_count = 0
        clipped_count = 0

        for iso3, cdf in idf.groupby("country_iso3", sort=True):
            history = cdf[cdf["indicator_value"].notna() & (cdf["year"] <= PANEL_END_YEAR)][["year", "indicator_value"]].copy()
            if history.empty:
                continue

            eligible += 1
            series = history.sort_values("year").copy()

            for year in range(FORECAST_START_YEAR, FORECAST_END_YEAR + 1):
                feat, fallback = build_feature_row(series, year)
                used_method = model_name

                if model_name == "carry_forward_baseline" or fitted is None:
                    pred = fallback
                else:
                    bundle, model_obj = fitted
                    feat_filled = feat.fillna(medians).fillna(fallback)
                    try:
                        pred = float(bundle.predict_fn(model_obj, feat_filled)[0])
                    except Exception:
                        pred = np.nan

                if pd.isna(pred):
                    pred = fallback
                    used_method = "carry_forward_baseline"
                    null_fallback_count += 1

                if pred < lower_bound or pred > upper_bound:
                    pred = float(min(max(pred, lower_bound), upper_bound))
                    clipped_count += 1

                prev = series.loc[series["year"] == year - 1, "indicator_value"]
                prev_value = float(prev.iloc[0]) if not prev.empty else fallback
                if abs(pred - prev_value) > max_jump:
                    pred = fallback
                    used_method = "carry_forward_baseline"
                    jump_fallback_count += 1

                series = pd.concat(
                    [series, pd.DataFrame([{"year": year, "indicator_value": pred}])],
                    ignore_index=True,
                )

                forecast_rows.append(
                    {
                        "country_iso3": iso3,
                        "year": year,
                        "scenario_id": "baseline_ml_dynamic_risk",
                        "indicator_name": indicator,
                        "projected_value": float(pred),
                        "projection_source": "world2045_structural_ml_sprint2b",
                        "forecast_method": used_method,
                        "model_version": "sprint2b_v1",
                        "created_at": now_utc,
                    }
                )

        expected_rows = eligible * (FORECAST_END_YEAR - FORECAST_START_YEAR + 1)
        actual_rows = sum(1 for r in forecast_rows if r["indicator_name"] == indicator)
        null_rows = sum(
            1
            for r in forecast_rows
            if r["indicator_name"] == indicator and pd.isna(r["projected_value"])
        )

        coverage_rows.append(
            {
                "indicator_name": indicator,
                "eligible_countries": eligible,
                "forecast_start_year": FORECAST_START_YEAR,
                "forecast_end_year": FORECAST_END_YEAR,
                "expected_rows": expected_rows,
                "actual_rows": actual_rows,
                "null_projection_rows": null_rows,
                "selected_model": model_name,
            }
        )

        sanity_rows.append(
            {
                "indicator_name": indicator,
                "selected_model": model_name,
                "lower_bound": lower_bound,
                "upper_bound": upper_bound,
                "max_yoy_jump": max_jump,
                "null_fallback_count": null_fallback_count,
                "jump_fallback_count": jump_fallback_count,
                "clipped_count": clipped_count,
            }
        )

    forecast_df = pd.DataFrame(forecast_rows).sort_values(["indicator_name", "country_iso3", "year"])
    coverage_df = pd.DataFrame(coverage_rows).sort_values("indicator_name")
    sanity_df = pd.DataFrame(sanity_rows).sort_values("indicator_name")

    return forecast_df, coverage_df, sanity_df


def run_training(data_root: Path, repo_root: Path, output_root: Path) -> dict[str, str]:
    output_root.mkdir(parents=True, exist_ok=True)

    indicator_wide = load_indicator_sources(data_root)
    regions = load_region_map(repo_root)
    panel = build_ml_panel(indicator_wide, regions)

    panel_path = output_root / "structural_risk_ml_panel_country_year.csv"
    panel.to_csv(panel_path, index=False)

    bundles = base_model_bundles()

    pred_rows = rolling_origin_predictions(panel, bundles)
    pred_rows_path = output_root / "rolling_origin_prediction_rows.csv"
    pred_rows.to_csv(pred_rows_path, index=False)

    fold_metrics, summary_metrics = summarize_predictions(pred_rows)
    fold_metrics_path = output_root / "rolling_origin_metrics.csv"
    fold_metrics.to_csv(fold_metrics_path, index=False)

    summary_metrics_path = output_root / "rolling_origin_metrics_summary.csv"
    summary_metrics.to_csv(summary_metrics_path, index=False)

    reg_metrics, reg_worse = regional_metrics(pred_rows)
    reg_metrics_path = output_root / "regional_metrics.csv"
    reg_metrics.to_csv(reg_metrics_path, index=False)

    reg_worse_path = output_root / "regional_ml_worse_than_carry_forward.csv"
    reg_worse.to_csv(reg_worse_path, index=False)

    decisions = selection_decisions(summary_metrics, fold_metrics)
    decisions_path = output_root / "model_selection_decision.csv"
    decisions.to_csv(decisions_path, index=False)

    thresholds = derive_sanity_thresholds(panel)
    thresholds_path = output_root / "forecast_sanity_thresholds.csv"
    thresholds.to_csv(thresholds_path, index=False)

    forecast_df, coverage_df, sanity_df = generate_forecasts(
        panel=panel,
        bundles=bundles,
        decisions=decisions,
        thresholds=thresholds,
    )

    forecast_path = output_root / "structural_risk_forecast_contract_2024_2045.csv"
    forecast_df.to_csv(forecast_path, index=False)

    coverage_path = output_root / "coverage_report_by_indicator.csv"
    coverage_df.to_csv(coverage_path, index=False)

    sanity_path = output_root / "forecast_sanity_report.csv"
    sanity_df.to_csv(sanity_path, index=False)

    summary_payload = {
        "panel_path": str(panel_path),
        "rolling_origin_prediction_rows_path": str(pred_rows_path),
        "rolling_origin_metrics_path": str(fold_metrics_path),
        "rolling_origin_metrics_summary_path": str(summary_metrics_path),
        "regional_metrics_path": str(reg_metrics_path),
        "regional_ml_worse_path": str(reg_worse_path),
        "selection_path": str(decisions_path),
        "sanity_thresholds_path": str(thresholds_path),
        "sanity_report_path": str(sanity_path),
        "coverage_path": str(coverage_path),
        "forecast_artifact_path": str(forecast_path),
        "sklearn_available": any("sklearn" in m.name for m in bundles),
        "model_candidates": ["carry_forward_baseline", *[m.name for m in bundles]],
    }

    summary_path = output_root / "run_summary.json"
    summary_path.write_text(json.dumps(summary_payload, indent=2), encoding="utf-8")

    return summary_payload


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Sprint 2B structural-risk ML forecasts")
    parser.add_argument(
        "--data-root",
        default="data",
        help="Root data directory containing raw/ and bronze/ subdirectories",
    )
    parser.add_argument(
        "--repo-root",
        default=".",
        help="Repository root for seed lookups",
    )
    parser.add_argument(
        "--output-dir",
        default="data/processed/ml",
        help="Directory for generated panel, metrics, coverage, and forecast artifacts",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    data_root = Path(args.data_root).resolve()
    repo_root = Path(args.repo_root).resolve()
    output_root = Path(args.output_dir).resolve()

    summary = run_training(data_root=data_root, repo_root=repo_root, output_root=output_root)

    print("Sprint 2B structural-risk training complete.")
    print(f"Forecast artifact: {summary['forecast_artifact_path']}")
    print(f"Rolling metrics: {summary['rolling_origin_metrics_path']}")
    print(f"Regional metrics: {summary['regional_metrics_path']}")
    print(f"Model candidates: {', '.join(summary['model_candidates'])}")
    print(f"sklearn_available: {summary['sklearn_available']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
