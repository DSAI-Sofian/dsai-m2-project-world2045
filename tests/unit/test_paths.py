from world2045.utils.paths import RAW_DIR, DBT_DIR


def test_raw_dir_name():
    assert RAW_DIR.name == "raw"


def test_dbt_dir_name():
    assert DBT_DIR.name == "dbt"
