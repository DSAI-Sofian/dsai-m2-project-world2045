from __future__ import annotations

import argparse
import subprocess
import sys
from shutil import which
from pathlib import Path


DEFAULT_SELECT = [
    "silver__dim_country",
    "silver__dim_year",
    "silver__fact_country_year_spine",
    "silver__fact_population_country_year",
    "gold__mart_world2045_features_country_year",
]


def run_dbt_build(
    dbt_project_dir: Path,
    select: list[str] | None = None,
    full_refresh: bool = False,
) -> None:
    if not dbt_project_dir.exists():
        raise FileNotFoundError(f"dbt project directory not found: {dbt_project_dir}")

    dbt_executable = which("dbt")
    if dbt_executable is None:
        candidates = [
            Path(sys.executable).resolve().parent / "dbt",
            Path(__file__).resolve().parents[1] / ".venv" / "bin" / "dbt",
            Path.cwd() / ".venv" / "bin" / "dbt",
        ]
        found = next((c for c in candidates if c.exists()), None)
        if found is not None:
            dbt_executable = str(found)
        else:
            raise FileNotFoundError(
                "dbt executable not found in PATH or known virtual environment locations."
            )

    command = [dbt_executable, "build"]

    if select:
        command.extend(["--select", *select])

    if full_refresh:
        command.append("--full-refresh")

    print(f"Running command in {dbt_project_dir}:")
    print(" ".join(command))

    subprocess.run(
        command,
        cwd=dbt_project_dir,
        check=True,
    )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run dbt build for the World in 2045 project."
    )
    parser.add_argument(
        "--project-dir",
        default="dbt",
        help="Path to the dbt project directory (default: dbt)",
    )
    parser.add_argument(
        "--full",
        action="store_true",
        help="Run full dbt build without model selection",
    )
    parser.add_argument(
        "--full-refresh",
        action="store_true",
        help="Pass --full-refresh to dbt build",
    )
    parser.add_argument(
        "--select",
        nargs="+",
        help="Optional explicit dbt model selection list",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    dbt_project_dir = Path(args.project_dir).resolve()

    if args.full:
        select = None
    elif args.select:
        select = args.select
    else:
        select = DEFAULT_SELECT

    try:
        run_dbt_build(
            dbt_project_dir=dbt_project_dir,
            select=select,
            full_refresh=args.full_refresh,
        )
        print("dbt build complete.")
    except subprocess.CalledProcessError as exc:
        print(f"dbt build failed with exit code {exc.returncode}")
        raise


if __name__ == "__main__":
    main()
