import pandas as pd

path = "data/raw/ssp/ssp_gdp_projection_raw.csv"

df = pd.read_csv(path)

# keep SSP2 only
df = df[df["scenario"] == "SSP2"]

# keep newest base year
df = df[df["unit"] == "billion USD_2017/yr"]

# identify year columns
year_cols = [c for c in df.columns if c.isdigit()]

df_long = df.melt(
    id_vars=["model","scenario","region","unit","variable","type"],
    value_vars=year_cols,
    var_name="year",
    value_name="gdp_real_billion_usd"
)

df_long["year"] = df_long["year"].astype(int)

df_long = df_long.rename(
    columns={
        "region": "country_name"
    }
)

# keep only years relevant to project
df_long = df_long[df_long["year"] >= 2024]

df_long.to_csv(
    "data/processed/ssp_gdp_country_year.csv",
    index=False
)

print("Rows:", len(df_long))
print("Countries:", df_long["country_name"].nunique())
print("Years:", df_long["year"].min(), df_long["year"].max())