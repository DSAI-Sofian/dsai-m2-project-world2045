from pathlib import Path
import pandas as pd

WID_DIR = Path("data/raw/wid")
STAGE_PATH = WID_DIR / "wid_country_year_stage.csv"
OUT_PATH = WID_DIR / "wid_inequality_extract.csv"

CHUNK_SIZE = 200_000


def main() -> None:
    if OUT_PATH.exists():
        OUT_PATH.unlink()

    first_write = True
    rows_written = 0

    share_percentiles = {"p0p50", "p90p100", "p99p100"}

    for chunk in pd.read_csv(
        STAGE_PATH,
        usecols=["country", "source_alpha2", "year", "variable", "percentile", "value"],
        chunksize=CHUNK_SIZE,
        low_memory=False,
    ):
        chunk["variable"] = chunk["variable"].astype(str).str.strip()
        chunk["percentile"] = chunk["percentile"].astype(str).str.strip()

        mask = (
            ((chunk["variable"] == "gptincj992") & (chunk["percentile"] == "p0p100"))
            |
            ((chunk["variable"] == "sptincj992") & (chunk["percentile"].isin(share_percentiles)))
        )

        filtered = chunk.loc[mask].copy()

        if filtered.empty:
            continue

        filtered.to_csv(
            OUT_PATH,
            mode="w" if first_write else "a",
            header=first_write,
            index=False,
        )
        rows_written += len(filtered)
        first_write = False

    print(f"Written: {OUT_PATH}")
    print(f"Rows written: {rows_written}")


if __name__ == "__main__":
    main()