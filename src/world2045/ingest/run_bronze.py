from pathlib import Path

from world2045.ingest.wpp import read_wpp_population_standard
from world2045.ingest.wdi import ingest_wdi


def main() -> None:
    bronze_root = Path("data/raw")

    print("Running Bronze ingestion...")

    wpp_path = bronze_root / "wpp2024" / "population_standard.csv"
    if not wpp_path.exists():
        raise FileNotFoundError(f"WPP file not found: {wpp_path}")

    wpp_df = read_wpp_population_standard(wpp_path)
    print(f"WPP rows available: {len(wpp_df)}")

    wdi_path = ingest_wdi(
        bronze_root=bronze_root,
        start_year=1960,
        end_year=2024,
    )
    print(f"WDI bronze written to: {wdi_path}")

    print("Bronze ingestion complete.")


if __name__ == "__main__":
    main()