import pandas as pd
import pytest

from world2045.quality.checks import assert_required_columns, duplicate_count


def test_assert_required_columns_passes():
    df = pd.DataFrame({"iso3": ["SGP"], "year": [2024]})
    assert_required_columns(df, ["iso3", "year"])


def test_assert_required_columns_fails():
    df = pd.DataFrame({"iso3": ["SGP"]})
    with pytest.raises(ValueError):
        assert_required_columns(df, ["iso3", "year"])


def test_duplicate_count():
    df = pd.DataFrame(
        {
            "iso3": ["SGP", "SGP"],
            "year": [2024, 2024],
        }
    )
    assert duplicate_count(df, ["iso3", "year"]) == 1
