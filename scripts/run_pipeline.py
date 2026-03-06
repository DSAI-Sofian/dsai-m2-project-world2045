from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]


def run_step(label: str, command: list[str]) -> None:
    print(f"\n{'=' * 72}")
    print(f"{label}")
    print(f"{'=' * 72}")
    print("Command:", " ".join(command))

    subprocess.run(
        command,
        cwd=REPO_ROOT,
        check=True,
    )

    print(f"{label} complete.")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run the World in 2045 Phase 1 pipeline."
    )
    parser.add_argument(
        "--skip-bronze",
        action="store_true",
        help="Skip scripts/run_bronze.py",
    )
    parser.add_argument(
        "--skip-load",
        action="store_true",
        help="Skip scripts/load_bronze_bigquery.py",
    )
    parser.add_argument(
        "--skip-dbt",
        action="store_true",
        help="Skip scripts/run_dbt_build.py",
    )
    parser.add_argument(
        "--full-refresh",
        action="store_true",
        help="Pass --full-refresh to scripts/run_dbt_build.py",
    )
    parser.add_argument(
        "--dbt-full",
        action="store_true",
        help="Run full dbt build instead of the default selected models",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()

    python_executable = sys.executable

    try:
        if not args.skip_bronze:
            run_step(
                "Step 1 - Bronze ingestion",
                [python_executable, "scripts/run_bronze.py"],
            )

        if not args.skip_load:
            run_step(
                "Step 2 - Bronze load to BigQuery",
                [python_executable, "scripts/load_bronze_bigquery.py"],
            )

        if not args.skip_dbt:
            dbt_command = [python_executable, "scripts/run_dbt_build.py"]

            if args.dbt_full:
                dbt_command.append("--full")

            if args.full_refresh:
                dbt_command.append("--full-refresh")

            run_step(
                "Step 3 - dbt build",
                dbt_command,
            )

        print(f"\n{'=' * 72}")
        print("Pipeline complete.")
        print(f"{'=' * 72}")

    except subprocess.CalledProcessError as exc:
        print(f"\nPipeline failed with exit code {exc.returncode}")
        raise


if __name__ == "__main__":
    main()