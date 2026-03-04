# World in 2045

A data‑engineering project that builds a reproducible analytics pipeline to model global development trajectories toward the year 2045.

## Objectives
- Construct a modern data platform using real-world datasets.
- Model historical development trends.
- Produce scenario-driven projections.

## Technology Stack

| Layer | Technology |
|------|------------|
| Storage | BigQuery |
| Transformation | dbt |
| CI/CD | GitHub Actions |
| Orchestration | Python pipelines |
| Version Control | Git + GitHub |

## Architecture Overview

Raw datasets are ingested into **Bronze** tables, normalized into **Silver** analytical datasets, and aggregated into **Gold** feature marts.

## Current Status

Phase 1 – Population backbone implemented.

Tables created:
- bronze__wpp2024__population_standard_raw
- bronze__wpp2024__population_standard
- silver__fact_population_country_year

Row count validated: ~18k rows.

## Repository Structure

dbt/
models/
silver/
facts/
gold/

data/
raw/

macros/

seeds/

## Next Milestone
Implement **World Development Indicators (WDI)** ingestion and silver modeling.