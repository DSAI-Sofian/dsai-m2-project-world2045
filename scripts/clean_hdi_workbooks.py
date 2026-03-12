from pathlib import Path
import re
import pandas as pd


RAW_DIR = Path("data/raw/hdi")
OUT_DIR = RAW_DIR

TABLE1_XLSX = RAW_DIR / "HDR25_Statistical_Annex_HDI_Table.xlsx"
TABLE2_XLSX = RAW_DIR / "HDR25_Statistical_Annex_HDI_Trends_Table.xlsx"

TABLE1_SHEET = "Table 1. HDI"
TABLE2_SHEET = "Table 2. HDI trends"


GROUP_LABELS = {
    "Very high human development",
    "High human development",
    "Medium human development",
    "Low human development",
    "Developing countries",
    "Least developed countries",
    "Small island developing states",
    "Organisation for Economic Co-operation and Development",
    "Regions",
    "World",
    "Notes",
}


def clean_text(x):
    if pd.isna(x):
        return None
    s = str(x).strip()
    return s if s else None


def is_group_or_break_row(country: str | None) -> bool:
    if country is None:
        return True
    c = country.strip()
    if c in GROUP_LABELS:
        return True
    if c.lower().startswith("note"):
        return True
    if c.lower().startswith("a ") or c.lower().startswith("b "):
        return True
    return False


def is_year_label(value) -> bool:
    """
    Return True when the column label is a 4-digit year such as 1990, 1991, ..., 2023.
    """
    if value is None:
        return False
    s = str(value).strip()
    return bool(re.fullmatch(r"\d{4}", s))


def flatten_multirow_header(header_rows: pd.DataFrame) -> list[str]:
    """
    Flatten a multi-row header by taking the last non-null token in each column.
    This works well for these HDI workbooks because the usable label is in the
    bottom-most populated header row for each metric column.
    """
    cols = []
    for col_idx in range(header_rows.shape[1]):
        tokens = []
        for row_idx in range(header_rows.shape[0]):
            val = header_rows.iat[row_idx, col_idx]
            val = clean_text(val)
            if val is not None:
                tokens.append(val)

        if not tokens:
            cols.append(f"col_{col_idx}")
            continue

        final = tokens[-1]

        if final == "Value":
            final = "hdi"
        elif final == "(years)":
            joined = " | ".join(tokens).lower()
            if "life expectancy" in joined:
                final = "life_expectancy_years"
            elif "expected years of schooling" in joined:
                final = "expected_years_schooling"
            elif "mean years of schooling" in joined:
                final = "mean_years_schooling"
        elif final == "(2021 PPP $)":
            final = "gni_per_capita_2021_ppp_usd"

        cols.append(final)

    seen = {}
    unique_cols = []
    for c in cols:
        if c not in seen:
            seen[c] = 0
            unique_cols.append(c)
        else:
            seen[c] += 1
            unique_cols.append(f"{c}_{seen[c]}")

    return unique_cols


def clean_table1_hdi() -> pd.DataFrame:
    """
    HDR25_Statistical_Annex_HDI_Table.xlsx
    Sheet: Table 1. HDI

    Based on observed workbook structure:
    0  = HDI rank
    1  = Country
    2  = HDI 2023
    4  = Life expectancy at birth (years) 2023
    6  = Expected years of schooling 2023
    8  = Mean years of schooling 2023
    10 = GNI per capita (2021 PPP $) 2023
    12 = GNI per capita rank minus HDI rank 2023
    14 = HDI rank 2022

    Odd/intermediate columns are footnote or spacer columns and should be ignored.
    """
    raw = pd.read_excel(TABLE1_XLSX, sheet_name=TABLE1_SHEET, header=None)

    data = raw.iloc[7:].copy().reset_index(drop=True)

    if data.shape[1] < 15:
        raise ValueError(
            f"Unexpected Table 1 column count: {data.shape[1]}. "
            "Expected at least 15 columns based on inspected workbook layout."
        )

    cleaned = pd.DataFrame({
        "hdi_rank_2023": data.iloc[:, 0],
        "country": data.iloc[:, 1],
        "hdi_2023": data.iloc[:, 2],
        "life_expectancy_years_2023": data.iloc[:, 4],
        "expected_years_schooling_2023": data.iloc[:, 6],
        "mean_years_schooling_2023": data.iloc[:, 8],
        "gni_per_capita_2023_ppp_usd": data.iloc[:, 10],
        "gni_rank_minus_hdi_rank_2023": data.iloc[:, 12],
        "hdi_rank_2022": data.iloc[:, 14],
    })

    cleaned["country"] = cleaned["country"].map(clean_text)
    cleaned = cleaned[~cleaned["country"].map(is_group_or_break_row)].copy()

    metric_cols = [c for c in cleaned.columns if c != "country"]
    for c in metric_cols:
        cleaned[c] = pd.to_numeric(cleaned[c], errors="coerce")

    cleaned = cleaned[cleaned["hdi_2023"].notna()].copy()
    cleaned = cleaned.reset_index(drop=True)
    return cleaned


def clean_table2_hdi_trends() -> tuple[pd.DataFrame, pd.DataFrame]:
    """
    HDR25_Statistical_Annex_HDI_Trends_Table.xlsx
    Sheet: Table 2. HDI trends

    Structure observed:
    - title / metadata rows above
    - row 4 contains the usable header
    - data starts at row 5
    - group rows break the country list

    Important:
    - Detect ALL year columns dynamically, not only selected snapshot years.
    """
    raw = pd.read_excel(TABLE2_XLSX, sheet_name=TABLE2_SHEET, header=None)

    header = raw.iloc[4].copy()
    cols = []
    for i, val in enumerate(header):
        val = clean_text(val)
        cols.append(val if val is not None else f"col_{i}")

    data = raw.iloc[5:].copy()
    data.columns = cols
    data = data.reset_index(drop=True)

    data["Country"] = data["Country"].map(clean_text)
    data = data[~data["Country"].map(is_group_or_break_row)].copy()

    year_cols = [c for c in data.columns if is_year_label(c)]
    year_cols = sorted(year_cols, key=lambda x: int(str(x)))

    if not year_cols:
        raise ValueError(
            "No year columns detected in HDI trends table. "
            "Check the workbook structure and header row."
        )

    rename_map = {
        "HDI rank": "hdi_rank_2023",
        "Country": "country",
        "2015-2023": "change_in_hdi_rank_2015_2023",
        "1990-2000": "avg_annual_hdi_growth_1990_2000_pct",
        "2000-2010": "avg_annual_hdi_growth_2000_2010_pct",
        "2010-2023": "avg_annual_hdi_growth_2010_2023_pct",
        "1990-2023": "avg_annual_hdi_growth_1990_2023_pct",
    }
    data = data.rename(columns=rename_map)

    year_rename_map = {str(y): f"hdi_{y}" for y in year_cols}
    data = data.rename(columns=year_rename_map)

    hdi_year_cols = [f"hdi_{y}" for y in year_cols]

    wanted = [
        "country",
        "hdi_rank_2023",
        *hdi_year_cols,
        "change_in_hdi_rank_2015_2023",
        "avg_annual_hdi_growth_1990_2000_pct",
        "avg_annual_hdi_growth_2000_2010_pct",
        "avg_annual_hdi_growth_2010_2023_pct",
        "avg_annual_hdi_growth_1990_2023_pct",
    ]
    present = [c for c in wanted if c in data.columns]
    data = data[present].copy()

    metric_cols = [c for c in data.columns if c != "country"]
    for c in metric_cols:
        data[c] = pd.to_numeric(data[c], errors="coerce")

    data = data[data[hdi_year_cols].notna().any(axis=1)].copy()
    data = data.reset_index(drop=True)

    long_df = data.melt(
        id_vars=["country"],
        value_vars=hdi_year_cols,
        var_name="metric_year",
        value_name="hdi",
    )

    long_df["year"] = (
        long_df["metric_year"]
        .str.replace("hdi_", "", regex=False)
        .astype(int)
    )
    long_df = long_df.drop(columns=["metric_year"])
    long_df = long_df[long_df["hdi"].notna()].copy()
    long_df = long_df.reset_index(drop=True)

    return data, long_df


def main():
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    table1 = clean_table1_hdi()
    table1_out = OUT_DIR / "hdi_table1_clean.csv"
    table1.to_csv(table1_out, index=False)

    table2_wide, table2_long = clean_table2_hdi_trends()
    table2_wide_out = OUT_DIR / "hdi_trends_table_wide_clean.csv"
    table2_long_out = OUT_DIR / "hdi_trends_table_long_clean.csv"

    table2_wide.to_csv(table2_wide_out, index=False)
    table2_long.to_csv(table2_long_out, index=False)

    print("Written:")
    print(f"  {table1_out}")
    print(f"  {table2_wide_out}")
    print(f"  {table2_long_out}")

    print("\nRow counts:")
    print(f"  table1_clean: {len(table1):,}")
    print(f"  table2_wide_clean: {len(table2_wide):,}")
    print(f"  table2_long_clean: {len(table2_long):,}")

    print("\nDetected HDI trend years:")
    detected_years = sorted(table2_long["year"].dropna().unique().tolist())
    print(detected_years)

    print("\nSample Table 1:")
    print(table1.head(10).to_string(index=False))

    print("\nSample Table 2 long:")
    print(table2_long.head(10).to_string(index=False))


if __name__ == "__main__":
    main()