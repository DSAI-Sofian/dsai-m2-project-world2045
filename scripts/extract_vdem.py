import zipfile
import pandas as pd
from pathlib import Path

zip_path = Path("data/raw/vdem/vdem.zip")
out_path = Path("data/raw/vdem/vdem_country_year.csv")

with zipfile.ZipFile(zip_path) as z:
    with z.open("V-Dem-CY-Full+Others-v15.csv") as f:

        df = pd.read_csv(
            f,
            usecols=[
                "country_name",
                "country_text_id",
                "year",
                "v2x_libdem",
                "v2x_polyarchy",
                "v2x_jucon",
                "v2x_civlib"
            ],
            low_memory=True
        )

out = pd.DataFrame({
    "country_name": df["country_name"],
    "country_text_id": df["country_text_id"],
    "country_iso3": df["country_text_id"].str.upper(),
    "year": df["year"],
    "vdem_liberal_democracy_index": df["v2x_libdem"],
    "vdem_electoral_democracy_index": df["v2x_polyarchy"],
    "vdem_judicial_constraints_index": df["v2x_jucon"],
    "vdem_civil_liberties_index": df["v2x_civlib"]
})

out["source_name"] = "V-Dem"
out["source_version"] = "v15"

out.to_csv(out_path, index=False)

print("Created:", out_path)
print("Rows:", len(out))
