from pathlib import Path
from google.cloud import bigquery


def load_csv_to_bigquery(
    csv_path: str | Path,
    table_id: str,
    write_disposition: str = "WRITE_TRUNCATE",
) -> None:

    csv_path = Path(csv_path)

    if not csv_path.exists():
        raise FileNotFoundError(f"CSV not found: {csv_path}")

    client = bigquery.Client()

    job_config = bigquery.LoadJobConfig(
        source_format=bigquery.SourceFormat.CSV,
        skip_leading_rows=1,
        autodetect=True,
        write_disposition=write_disposition,
    )

    with open(csv_path, "rb") as f:
        job = client.load_table_from_file(
            f,
            table_id,
            job_config=job_config,
        )

    job.result()

    print(f"Loaded {csv_path} → {table_id}")