import pandas as pd

df = pd.read_csv(
    "data/raw/wpp2024/wpp2024_population_standard.csv",
    skiprows=16,
    usecols=["Year", "Variant"],
    low_memory=False,
)

print("min_year:", df["Year"].min())
print("max_year:", df["Year"].max())
print(df["Variant"].value_counts(dropna=False).head(20))
