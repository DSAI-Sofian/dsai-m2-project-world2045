from __future__ import annotations

import time
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable

import pandas as pd
import requests


BASE_URL = "https://api.worldbank.org/v2/country/all/indicator/{indicator}"
DEFAULT_TIMEOUT = 120
MAX_RETRIES = 5
REQUEST_SLEEP = 0.2


@dataclass(frozen=True)
class WDIIndicator:
    code: str
    name: str


WDI_MVP_INDICATORS: list[WDIIndicator] = [
    WDIIndicator("NY.GDP.MKTP.CD", "GDP, current US$"),
    WDIIndicator("NY.GDP.PCAP.CD", "GDP per capita, current US$"),
    WDIIndicator("NY.GDP.MKTP.KD.ZG", "GDP growth (annual %)"),
    WDIIndicator("SL.UEM.TOTL.ZS", "Unemployment, total (% of total labor force)"),
    WDIIndicator("FP.CPI.TOTL.ZG", "Inflation, consumer prices (annual %)"),
    WDIIndicator("SP.DYN.LE00.IN", "Life expectancy at birth, total (years)"),
    WDIIndicator("SH.DYN.MORT", "Mortality rate, under-5 (per 1,000 live births)"),
    WDIIndicator("SE.SEC.ENRR", "School enrollment, secondary (% gross)"),
    WDIIndicator("IT.NET.USER.ZS", "Individuals using the Internet (% of population)"),
    WDIIndicator("EG.ELC.ACCS.ZS", "Access to electricity (% of population)"),
    WDIIndicator("SI.POV.LMIC", "Poverty headcount ratio at $3.65/day (2017 PPP) (% of population)"),
]


def _safe_iso3(country_payload: dict) -> str | None:
    value = (country_payload or {}).get("id")

    if not isinstance(value, str):
        return None

    return value.upper()


def _request_with_retry(
    session: requests.Session,
    url: str,
    params: dict,
) -> requests.Response:
    retries = 0

    while retries < MAX_RETRIES:
        try:
            response = session.get(
                url,
                params=params,
                timeout=DEFAULT_TIMEOUT,
            )
            response.raise_for_status()
            return response

        except requests.exceptions.RequestException as exc:
            retries += 1

            if retries >= MAX_RETRIES:
                raise

            wait = 2 ** retries
            print(f"WDI request retry {retries}/{MAX_RETRIES} after {wait}s ({exc})")
            time.sleep(wait)

    raise RuntimeError("Unexpected retry failure state")


def _fetch_indicator_rows(
    indicator_code: str,
    start_year: int | None,
    end_year: int | None,
    session: requests.Session,
) -> list[dict]:

    rows: list[dict] = []
    page = 1

    while True:

        params = {
            "format": "json",
            "page": page,
            "per_page": 1000,
        }

        response = _request_with_retry(
            session=session,
            url=BASE_URL.format(indicator=indicator_code),
            params=params,
        )

        payload = response.json()

        # invalid indicator response
        if isinstance(payload, list) and len(payload) == 1 and "message" in payload[0]:
            raise ValueError(f"Indicator unavailable: {indicator_code}")

        if not isinstance(payload, list) or len(payload) != 2:
            raise ValueError(f"Unexpected API response for {indicator_code}: {payload}")

        meta, data = payload

        if not data:
            break

        for rec in data:

            value = rec.get("value")
            if value is None:
                continue

            try:
                year = int(rec.get("date"))
            except (TypeError, ValueError):
                continue

            if start_year and year < start_year:
                continue

            if end_year and year > end_year:
                continue

            country = rec.get("country") or {}
            indicator = rec.get("indicator") or {}

            iso3c = _safe_iso3(country)
            if iso3c is None:
                continue

            rows.append(
                {
                    "source_system": "wdi",
                    "dataset_code": "world_development_indicators",
                    "country_id": country.get("id"),
                    "country_name": country.get("value"),
                    "iso3c": iso3c,
                    "year": year,
                    "indicator_id": indicator.get("id") or indicator_code,
                    "indicator_name": indicator.get("value"),
                    "value": value,
                    "unit": rec.get("unit"),
                    "obs_status": rec.get("obs_status"),
                    "decimal": rec.get("decimal"),
                }
            )

        total_pages = int(meta.get("pages", 1))

        if page >= total_pages:
            break

        page += 1
        time.sleep(0.2)

    return rows


def ingest_wdi(
    bronze_root: str | Path,
    indicators: Iterable[WDIIndicator] | None = None,
    start_year: int | None = 1960,
    end_year: int | None = None,
    output_filename: str = "wdi_country_year_long.csv",
) -> Path:
    bronze_root = Path(bronze_root)
    out_dir = bronze_root / "wdi"
    out_dir.mkdir(parents=True, exist_ok=True)

    indicator_list = list(indicators or WDI_MVP_INDICATORS)

    session = requests.Session()
    all_rows: list[dict] = []
    skipped_indicators: list[str] = []

    for indicator in indicator_list:
        print(f"Fetching WDI indicator: {indicator.code} - {indicator.name}")

        try:
            rows = _fetch_indicator_rows(
                indicator_code=indicator.code,
                start_year=start_year,
                end_year=end_year,
                session=session,
            )
        except Exception as exc:
            print(f"Skipping indicator {indicator.code}: {exc}")
            skipped_indicators.append(indicator.code)
            continue

        all_rows.extend(rows)

    if not all_rows:
        raise ValueError("No WDI rows fetched.")

    df = pd.DataFrame(all_rows)

    df["year"] = pd.to_numeric(df["year"], errors="coerce").astype("Int64")
    df["value"] = pd.to_numeric(df["value"], errors="coerce")
    df["decimal"] = pd.to_numeric(df["decimal"], errors="coerce").astype("Int64")
    df["iso3c"] = df["iso3c"].astype("string").str.upper().str.strip()
    df["ingested_at"] = datetime.now(timezone.utc).isoformat()

    df = (
        df.dropna(subset=["iso3c", "year", "indicator_id"])
        .sort_values(["iso3c", "year", "indicator_id"])
        .drop_duplicates(subset=["iso3c", "year", "indicator_id"], keep="last")
        .reset_index(drop=True)
    )

    output_path = out_dir / output_filename
    df.to_csv(output_path, index=False)

    print(f"WDI rows written: {len(df)}")
    print(f"WDI output written to: {output_path}")

    if skipped_indicators:
        print(f"Skipped indicators: {', '.join(skipped_indicators)}")

    return output_path