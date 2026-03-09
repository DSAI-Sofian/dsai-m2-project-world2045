from __future__ import annotations

import csv
import re
from pathlib import Path

from world2045.load.bigquery import load_csv_to_bigquery


PROJECT_ID = "project-93ce72dd-0a39-4d93-bf5"
BQ_DATASET = "world2045_ci"
BRONZE_ROOT = Path("data/raw")
TMP_ROOT = Path("data/tmp")
TMP_ROOT.mkdir(parents=True, exist_ok=True)


BRONZE_LOADS = [
    {
        "name": "wpp2024_f01_sheet1_clean",
        "csv_path": BRONZE_ROOT / "wpp2024" / "csv_clean" / "wpp2024_f01_sheet1_clean.csv",
        "table_name": "bronze__wpp2024__f01_sheet1_clean",
    },
    {
        "name": "wpp2024_f01_sheet2_clean",
        "csv_path": BRONZE_ROOT / "wpp2024" / "csv_clean" / "wpp2024_f01_sheet2_clean.csv",
        "table_name": "bronze__wpp2024__f01_sheet2_clean",
    },
    {
        "name": "wdi_country_year_long",
        "csv_path": BRONZE_ROOT / "wdi" / "wdi_country_year_long.csv",
        "table_name": "bronze__wdi_country_year_long",
    },
]


def sanitize_column_name(name: str) -> str:
    name = name.strip().lower()

    replacements = {
        "%": "pct",
        "#": "num",
        "&": "and",
        "+": "plus",
    }
    for old, new in replacements.items():
        name = name.replace(old, new)

    name = re.sub(r"[^a-z0-9]+", "_", name)
    name = re.sub(r"_+", "_", name).strip("_")

    if not name:
        name = "col"

    if name[0].isdigit():
        name = f"col_{name}"

    return name


def make_unique(names: list[str]) -> list[str]:
    seen: dict[str, int] = {}
    out: list[str] = []

    for name in names:
        if name not in seen:
            seen[name] = 0
            out.append(name)
        else:
            seen[name] += 1
            out.append(f"{name}_{seen[name]}")

    return out


def write_sanitized_csv(src: Path, dst: Path) -> None:
    with src.open("r", encoding="utf-8-sig", newline="") as fin, dst.open(
        "w", encoding="utf-8", newline=""
    ) as fout:
        reader = csv.reader(fin)
        writer = csv.writer(fout)

        header = next(reader)
        clean_header = make_unique([sanitize_column_name(col) for col in header])
        writer.writerow(clean_header)

        for row in reader:
            writer.writerow(row)


def main() -> None:
    print("Loading Bronze datasets to BigQuery...")

    for item in BRONZE_LOADS:
        dataset_name = item["name"]
        csv_path = item["csv_path"]
        table_name = item["table_name"]

        if not csv_path.exists():
            print(f"Skipping {dataset_name}: file not found -> {csv_path}")
            continue

        staged_csv_path = TMP_ROOT / f"{dataset_name}__sanitized.csv"
        write_sanitized_csv(csv_path, staged_csv_path)

        table_id = f"{PROJECT_ID}.{BQ_DATASET}.{table_name}"

        print(f"Loading {dataset_name} from {staged_csv_path} -> {table_id}")
        load_csv_to_bigquery(
            csv_path=staged_csv_path,
            table_id=table_id,
            write_disposition="WRITE_TRUNCATE",
        )

    print("Bronze BigQuery load complete.")


if __name__ == "__main__":
    main()