from __future__ import annotations

from pathlib import Path

from world2045.load.bigquery import load_csv_to_bigquery


PROJECT_ID = "project-93ce72dd-0a39-4d93-bf5"
BQ_DATASET = "world2045_ci"
BRONZE_ROOT = Path("data/raw")


BRONZE_LOADS = [
    {
        "name": "wpp2024_population_standard",
        "csv_path": BRONZE_ROOT / "wpp2024" / "population_standard.csv",
        "table_name": "bronze__wpp2024__population_standard",
    },
    {
        "name": "wdi_country_year_long",
        "csv_path": BRONZE_ROOT / "wdi" / "wdi_country_year_long.csv",
        "table_name": "bronze__wdi_country_year_long",
    },
]


def main() -> None:
    print("Loading Bronze datasets to BigQuery...")

    for item in BRONZE_LOADS:
        dataset_name = item["name"]
        csv_path = item["csv_path"]
        table_name = item["table_name"]

        if not csv_path.exists():
            print(f"Skipping {dataset_name}: file not found -> {csv_path}")
            continue

        table_id = f"{PROJECT_ID}.{BQ_DATASET}.{table_name}"

        print(f"Loading {dataset_name}...")
        load_csv_to_bigquery(
            csv_path=csv_path,
            table_id=table_id,
            write_disposition="WRITE_TRUNCATE",
        )

    print("Bronze BigQuery load complete.")


if __name__ == "__main__":
    main()