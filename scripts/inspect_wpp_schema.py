import pandas as pd
from pathlib import Path

file_path = Path("data/raw/wpp2024/wpp2024_population_standard.csv")

df = pd.read_csv(
    file_path,
    skiprows=16,   # skip lines 1-16
    header=1,      # use line 18 as header (after skip)
    nrows=5
)

print("\nColumns detected:\n")
for c in df.columns:
    print(repr(c))

print("\nPreview:\n")
print(df.to_string(index=False))
