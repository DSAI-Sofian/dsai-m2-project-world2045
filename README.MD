# World in 2045

The World2045 platform analyzes long‑term global development trajectories across countries from 1950–2045.  

The platform integrates multiple global datasets including population, economic indicators, inequality metrics, governance indicators, climate vulnerability, conflict data, and human development indices.

## Objectives

1. Analyze past data (post–World War 2)
2. Review historical trends to predict future development
3. Develop a snapshot of the world in 2045
4. Propose actions to encourage positive growth and remediate negative trajectories

## Technology Stack

| Layer | Technology |
|------|------------|
| Storage | BigQuery |
| Transformation | dbt |
| CI/CD | GitHub Actions |
| Orchestration | Python pipelines |
| Version Control | Git + GitHub |

## Platform Architecture

The warehouse follows a **modern ELT layered architecture**.

```
Raw Data Sources
       ↓
Bronze Layer
(raw ingestion)
       ↓
Silver Layer
(conformed normalized warehouse)
       ↓
Gold Layer
(analytical feature marts)
```

## Repository Structure

## Domains Integrated

- Population (UN WPP)
- Economy (WDI)
- Inequality (WID)
- Human Development (HDI)
- Governance (V‑Dem)
- Climate (ND‑GAIN)
- Conflict (UCDP)

## Current Status

---

More details are available in TECHNICAL_README.MD

It provides detailed information on each of the sections below to guide developers and users working on the World2045 data platform.

It covers various aspects such as:

- Environment setup
- Naming conventions
- Partition strategy
- Data models
- Technology stack components
- dbt structure
- Python ingestion framework
- Development workflow
- Layers (Bronze, Silver, Gold)
- Ingestion best practices
- dbt testing strategy
- Future technical enhancements