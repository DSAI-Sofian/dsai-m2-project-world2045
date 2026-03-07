from pathlib import Path

from world2045.ingest.vdem import ingest_vdem_from_zip
from world2045.ingest.wpp import read_wpp_population_standard
from world2045.ingest.wdi import ingest_wdi


def main() -> None:
    bronze_root = Path("data/raw")

    print("Running Bronze ingestion...")

    # -------------------------
    # WPP population
    # -------------------------
    wpp_df = read_wpp_population_standard(
        bronze_root / "wpp2024" / "wpp2024_population_standard.csv"
    )
    print(f"WPP rows available: {len(wpp_df)}")

    # -------------------------
    # WDI indicators
    # -------------------------
    wdi_path = ingest_wdi(
        bronze_root=bronze_root,
        start_year=1960,
        end_year=2024,
    )
    print(f"WDI bronze written to: {wdi_path}")

    # -------------------------
    # V-Dem governance
    # -------------------------
    vdem_zip_path = bronze_root / "vdem" / "vdem.zip"

    if not vdem_zip_path.exists():
        raise FileNotFoundError(f"V-Dem ZIP not found: {vdem_zip_path}")

    vdem_path = ingest_vdem_from_zip(
        local_zip_path=str(vdem_zip_path),
        bronze_root=str(bronze_root),
    )

    print(f"V-Dem bronze written to: {vdem_path}")

    print("Bronze ingestion complete.")


if __name__ == "__main__":
    main()