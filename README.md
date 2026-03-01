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

## 2) Configure dbt profile

```yaml
world2045:
  target: dev
  outputs:
    dev:
      type: bigquery
      method: oauth
      project: YOUR_GCP_PROJECT_ID
      dataset: world2045_dev
      threads: 4
      location: US
```

## 3) GitHub Actions YAML for dbt CI

This is a **minimal** CI that:
- installs Python + dbt adapter
- writes a dbt profile from GitHub Secrets
- runs `dbt deps` and `dbt build`

### Required GitHub Secrets (recommended)
Create these in **Repo → Settings → Secrets and variables → Actions**:
- `DBT_PROFILES_YML` (full contents of `profiles.yml`)
- Optionally: `DBT_PROJECT_DIR` (default `dbt` if omitted)

> This avoids committing credentials and avoids trying to use local `~/.dbt/profiles.yml`.

Create: `.github/workflows/dbt-ci.yml`

```yaml
```yaml
name: dbt CI

on:
  pull_request:
    branches: [ "main", "develop" ]
  push:
    branches: [ "main" ]

jobs:
  dbt-build:
    runs-on: ubuntu-latest

    env:
      DBT_PROJECT_DIR: ${{ secrets.DBT_PROJECT_DIR || 'dbt' }}
      DBT_PROFILES_DIR: ${{ github.workspace }}/.dbt

    steps:
      - name: Checkout
        uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: "3.11"

      - name: Install dbt
        run: |
          python -m pip install --upgrade pip
          # Choose ONE adapter. BigQuery example:
          pip install "dbt-bigquery==1.8.*"

      - name: Write dbt profiles.yml from secret
        run: |
          mkdir -p "${DBT_PROFILES_DIR}"
          echo "${{ secrets.DBT_PROFILES_YML }}" > "${DBT_PROFILES_DIR}/profiles.yml"

      - name: dbt deps
        working-directory: ${{ env.DBT_PROJECT_DIR }}
        run: dbt deps

      - name: dbt debug
        working-directory: ${{ env.DBT_PROJECT_DIR }}
        run: dbt debug

      - name: dbt build
        working-directory: ${{ env.DBT_PROJECT_DIR }}
        run: dbt build
```

## 4) Initialize repo
