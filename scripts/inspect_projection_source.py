#!/usr/bin/env python3
"""Lightweight inspection utility for forecast projection source files.

Purpose:
- Inspect CSV or ZIP contents before building ingestion logic.
- Print file-level metadata and a small schema preview.
- Keep memory usage low by sampling rows only.

Usage examples:
    python scripts/inspect_projection_source.py data/raw/wpp/WPP2024_TotalPopulationByCountry.csv
    python scripts/inspect_projection_source.py data/raw/ssp/ssp_gdp.zip --sample-rows 5
"""

from __future__ import annotations

import argparse
import csv
import io
import sys
import zipfile
from pathlib import Path
from typing import Iterable


def sniff_csv_columns(path_or_buffer: io.TextIOBase, sample_rows: int = 5) -> tuple[list[str], list[list[str]]]:
    reader = csv.reader(path_or_buffer)
    try:
        header = next(reader)
    except StopIteration:
        return [], []
    rows: list[list[str]] = []
    for i, row in enumerate(reader):
        rows.append(row)
        if i + 1 >= sample_rows:
            break
    return header, rows


def inspect_csv(path: Path, sample_rows: int) -> None:
    print(f"[csv] {path}")
    print(f"size_bytes={path.stat().st_size}")
    with path.open("r", encoding="utf-8-sig", newline="") as f:
        header, rows = sniff_csv_columns(f, sample_rows=sample_rows)
    print(f"columns={len(header)}")
    print("header=")
    for col in header:
        print(f"  - {col}")
    print("sample_rows=")
    for row in rows:
        print(f"  - {row}")


def inspect_zip(path: Path, sample_rows: int) -> None:
    print(f"[zip] {path}")
    print(f"size_bytes={path.stat().st_size}")
    with zipfile.ZipFile(path) as zf:
        members = zf.infolist()
        print("members=")
        for member in members:
            print(f"  - {member.filename} ({member.file_size} bytes)")
        csv_members = [m for m in members if m.filename.lower().endswith(".csv")]
        if not csv_members:
            return
        print("\npreview_first_csv=")
        first = csv_members[0]
        with zf.open(first) as fh:
            text = io.TextIOWrapper(fh, encoding="utf-8-sig", newline="")
            header, rows = sniff_csv_columns(text, sample_rows=sample_rows)
        print(f"file={first.filename}")
        print(f"columns={len(header)}")
        print("header=")
        for col in header:
            print(f"  - {col}")
        print("sample_rows=")
        for row in rows:
            print(f"  - {row}")


def main(argv: Iterable[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("source_path", help="Path to a CSV or ZIP file")
    parser.add_argument("--sample-rows", type=int, default=5)
    args = parser.parse_args(argv)

    path = Path(args.source_path)
    if not path.exists():
        raise FileNotFoundError(f"Source not found: {path}")

    suffix = path.suffix.lower()
    if suffix == ".csv":
        inspect_csv(path, sample_rows=args.sample_rows)
    elif suffix == ".zip":
        inspect_zip(path, sample_rows=args.sample_rows)
    else:
        raise ValueError(f"Unsupported file type: {suffix}. Expected .csv or .zip")
    return 0


if __name__ == "__main__":
    sys.exit(main())
