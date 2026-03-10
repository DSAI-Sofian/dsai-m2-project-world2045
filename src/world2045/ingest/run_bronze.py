from pathlib import Path

from world2045.ingest.ucdp import ingest_ucdp
from world2045.ingest.nd_gain import ingest_nd_gain
from world2045.ingest.vdem import ingest_vdem_from_zip
from world2045.ingest.wpp import read_wpp_population_standard
from world2045.ingest.wdi import ingest_wdi


def main() -> None:
    raw_root = Path("data/raw")
    bronze_root = Path("data/bronze")

    print("Running Bronze ingestion...")

    wpp_path = raw_root / "wpp2024" / "wpp2024_population_standard.csv"
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

    vdem_csv_path = raw_root / "vdem" / "vdem_country_year.csv"
    vdem_zip_path = raw_root / "vdem" / "vdem.zip"

    if vdem_csv_path.exists():
        print(f"V-Dem country-year CSV already available, skipping ZIP ingestion: {vdem_csv_path}")
    elif vdem_zip_path.exists():
        vdem_path = ingest_vdem_from_zip(
            local_zip_path=str(vdem_zip_path),
            bronze_root=str(bronze_root),
        )
        print(f"V-Dem bronze written to: {vdem_path}")
    else:
        print(f"V-Dem source not found, skipping: {vdem_csv_path} / {vdem_zip_path}")

    nd_gain_path = ingest_nd_gain(
        raw_root=raw_root / "nd_gain",
        bronze_root=bronze_root,
    )
    
    ucdp_path = ingest_ucdp(
    raw_root=raw_root / "ucdp",
    bronze_root=bronze_root,
)
    print(f"ND-GAIN bronze written to: {nd_gain_path}")
    
    print(f"UCDP bronze written to: {ucdp_path}")

    print("Bronze ingestion complete.")


if __name__ == "__main__":
    main()