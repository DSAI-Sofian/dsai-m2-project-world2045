from pathlib import Path
from collections import defaultdict
import pandas as pd


WID_DIR = Path("data/raw/wid")
COUNTRIES_PATH = WID_DIR / "WID_countries.csv"
STAGE_PATH = WID_DIR / "wid_country_year_stage.csv"
CATALOG_PATH = WID_DIR / "wid_variable_catalog.csv"

CHUNK_SIZE = 200_000


def build_keep_codes() -> list[str]:
    df = pd.read_csv(COUNTRIES_PATH, sep=";", low_memory=False)
    df["alpha2"] = df["alpha2"].astype(str).str.strip()
    df["region"] = df["region"].fillna("").astype(str).str.strip()

    exclude_codes = {"AN", "CS", "DD", "SU", "YU", "ZZ"}

    keep = df[
        df["alpha2"].str.match(r"^[A-Z]{2}$", na=False)
        & df["region"].ne("")
        & ~df["alpha2"].isin(exclude_codes)
        & ~df["alpha2"].str.match(r"^[QOX]", na=False)
        & df["alpha2"].ne("WO")
    ].copy()

    keep_codes = sorted(keep["alpha2"].unique().tolist())
    return keep_codes


def rebuild_stage_file_if_missing() -> None:
    if STAGE_PATH.exists():
        print(f"Stage file already exists: {STAGE_PATH}")
        return

    keep_codes = build_keep_codes()
    print(f"Rebuilding stage file from {len(keep_codes)} keep codes...")

    first_write = True
    files_processed = 0
    rows_written = 0
    sample_columns_printed = False

    for code in keep_codes:
        path = WID_DIR / f"WID_data_{code}.csv"
        if not path.exists():
            continue

        try:
            for chunk in pd.read_csv(
                path,
                sep=";",
                chunksize=CHUNK_SIZE,
                low_memory=False
            ):
                chunk.columns = [c.strip() for c in chunk.columns]

                if not sample_columns_printed:
                    print("Sample columns from first readable file:")
                    print(chunk.columns.tolist())
                    sample_columns_printed = True

                # Keep only expected core columns if present
                wanted = [
                    "country",
                    "variable",
                    "percentile",
                    "year",
                    "value",
                    "age",
                    "pop",
                ]
                cols_present = [c for c in wanted if c in chunk.columns]
                chunk = chunk[cols_present].copy()
                chunk["source_alpha2"] = code

                chunk.to_csv(
                    STAGE_PATH,
                    mode="w" if first_write else "a",
                    header=first_write,
                    index=False,
                )

                rows_written += len(chunk)
                first_write = False

            files_processed += 1
            print(f"Processed: {path.name}")

        except Exception as e:
            print(f"Skipped {path.name}: {e}")

    print("\nStage rebuild complete.")
    print(f"Files processed: {files_processed}")
    print(f"Rows written: {rows_written}")
    print(f"Output: {STAGE_PATH}")


def build_variable_catalog() -> None:
    if not STAGE_PATH.exists():
        raise FileNotFoundError(f"Stage file not found: {STAGE_PATH}")

    catalog = defaultdict(lambda: {"rows": 0, "percentiles": set()})

    for chunk in pd.read_csv(
        STAGE_PATH,
        usecols=["variable", "percentile"],
        chunksize=CHUNK_SIZE,
        low_memory=False
    ):
        chunk["variable"] = chunk["variable"].astype(str).str.strip()
        chunk["percentile"] = chunk["percentile"].astype(str).str.strip()

        counts = chunk["variable"].value_counts()
        grouped = chunk.groupby("variable")["percentile"].agg(
            lambda x: sorted(set(x.dropna()))
        )

        for var, cnt in counts.items():
            catalog[var]["rows"] += int(cnt)

        for var, pct_list in grouped.items():
            catalog[var]["percentiles"].update(pct_list)

    rows = []
    for var, info in catalog.items():
        rows.append(
            {
                "variable": var,
                "row_count": info["rows"],
                "percentiles_sample": ",".join(sorted(info["percentiles"])[:30]),
            }
        )

    out = pd.DataFrame(rows).sort_values("variable")
    out.to_csv(CATALOG_PATH, index=False)

    print(f"\nCatalog written: {CATALOG_PATH}")
    print("\nFirst 50 catalog rows:")
    print(out.head(50).to_string(index=False))


def print_targeted_candidates() -> None:
    if not CATALOG_PATH.exists():
        raise FileNotFoundError(f"Catalog file not found: {CATALOG_PATH}")

    df = pd.read_csv(CATALOG_PATH, low_memory=False)

    patterns = ("gini", "ptinc", "diinc", "fiinc", "hweal", "shweal", "sptinc", "sdiinc")
    mask = df["variable"].astype(str).str.contains("|".join(patterns), case=False, na=False)

    candidates = df.loc[mask].sort_values("variable")

    print("\nLikely inequality-related variable codes:")
    if candidates.empty:
        print("No matching variables found.")
    else:
        print(candidates.to_string(index=False))


def main() -> None:
    print("=== WID recovery + catalog ===")
    rebuild_stage_file_if_missing()
    build_variable_catalog()
    print_targeted_candidates()
    print("\nDone.")


if __name__ == "__main__":
    main()