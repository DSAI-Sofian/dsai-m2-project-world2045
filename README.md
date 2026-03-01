# World in 2045 (Module 2) — Data Engineering + Forecasting

This repository contains the end-to-end data engineering and analytics workflow to answer:

> **What does the world look like in 2045?**

It implements a reproducible pipeline:
- **Bronze**: raw ingestion (immutable)
- **Silver**: conformed, cleaned, standardized (Country-Year contract)
- **Gold**: analytics-ready marts and forecast features
- **dbt**: transformations + tests + documentation

---

## Repository Structure
world-in-2045/
├── src/world2045/ # Python ingestion + utilities
├── dbt/ # dbt project (models, tests, macros)
├── data_contracts/ # transformation contracts (schema specs)
├── docs/ # blueprint + notes
└── infrastructure/ # IaC (optional: Terraform)


---

## Prerequisites

- Python 3.11+
- dbt (adapter depends on warehouse)
  - BigQuery: `dbt-bigquery`
- Google Cloud authentication (ADC recommended)

---

## Quickstart

### 1) Create environment

```bash
python -m venv .venv
# Windows:
# .venv\Scripts\activate
# macOS/Linux:
source .venv/bin/activate

pip install -U pip
pip install -r requirements.txt
```
