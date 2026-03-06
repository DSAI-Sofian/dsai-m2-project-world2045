from pathlib import Path
import pandas as pd

from world2045.utils.io import read_csv_safe
from world2045.quality.checks import assert_non_empty


def read_wpp_population_standard(
    path: str | Path = "data/raw/wpp2024/wpp2024_population_standard.csv",
) -> pd.DataFrame:
    df = read_csv_safe(path)
    assert_non_empty(df, "WPP population standard file")
    return df
