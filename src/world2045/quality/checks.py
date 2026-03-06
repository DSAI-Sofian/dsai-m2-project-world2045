import pandas as pd


def assert_required_columns(df: pd.DataFrame, required_columns: list[str]) -> None:
    missing = [c for c in required_columns if c not in df.columns]
    if missing:
        raise ValueError(f"Missing required columns: {missing}")


def assert_non_empty(df: pd.DataFrame, df_name: str = "dataframe") -> None:
    if df.empty:
        raise ValueError(f"{df_name} is empty")


def duplicate_count(df: pd.DataFrame, subset: list[str]) -> int:
    return int(df.duplicated(subset=subset).sum())
