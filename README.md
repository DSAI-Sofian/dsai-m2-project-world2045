# WORLD IN 2045

'World in 2045' is a country-year data engineering and analytics project that studies long-run development patterns from 1950 to 2045. It integrates population, economic, health, governance, climate, conflict, inequality, and human-development indicators into a unified BigQuery + dbt analytical platform.

- [WORLD IN 2045](#world-in-2045)
  - [Project objective](#project-objective)
  - [Repository Structure](#repository-structure)
  - [Core analytical outputs](#core-analytical-outputs)
  - [High-level architecture](#high-level-architecture)
  - [Main datasets used](#main-datasets-used)
  - [Time coverage](#time-coverage)
  - [Forecast interpretation](#forecast-interpretation)
  - [How to run the project](#how-to-run-the-project)
- [Live Dashboard](#live-dashboard)
  - [Quick Start](#quick-start)
  - [Intended audiences (external)](#intended-audiences-external)
  - [Intended audiences (coursework)](#intended-audiences-coursework)
- [Running the Local Analysis Notebook](#running-the-local-analysis-notebook)
  - [Repository structure required](#repository-structure-required)
  - [Quick Start (3 Commands)](#quick-start-3-commands)
  - [Local Analytical Notebook Architecture](#local-analytical-notebook-architecture)
  - [Architecture overview](#architecture-overview)
  - [Step-by-step workflow](#step-by-step-workflow)
  - [Project Structure (notebook section)](#project-structure-notebook-section)
  - [Reproducibility](#reproducibility)
- [Acknowledgements](#acknowledgements)


## Project objective

The project asks a practical question:

**Which countries are likely to strengthen, sustain, or struggle in their development trajectory by 2045?**

To answer that, the project builds:

- a conformed country-year warehouse
- a wide analytical feature mart
- a historical trajectory score
- a forecast scenario trajectory score for 2024-2045
- strategic ranking layers for rise potential and momentum
- quadrant segmentation for country positioning

## Repository Structure

```
MAIN
│
├── README.md
├── TECHNICAL_README.md
├── WORLD2045_BLUEPRINT_ORIGINAL.md
├── FINAL_ANALYTICAL_FINDINGS.md
├── DOOMSDAY_CLOCK_PROJECTION_2045.md
├── requirements.txt
├── pyproject.toml
│
├── configs/
├── docs/
│   ├ CHANGELOG.md
│   ├ WORLD2045_Streamlit_Deployment_Manual.md
│   ├ WORLD2045_Streamlit_Deployment_Training_Manual.md
│   └ WORLD2045_Training_Manual_Data_Analyst.md
│
├── src/
├── scripts/
├── tests/
│
├── dbt/
│
├── dashboard
│   ├ app/
│   └ data/
│
├── notebook/
│   └ WORLD2045_Training_Manual_Data_Analyst.ipynb
│
└ data/          (small extracts only)
```

## Core analytical outputs

The main analytical models are:

- `gold__country_trajectory_score_year`
- `gold__country_trajectory_score_year_scenario`
- `gold__region_trajectory_score_year`
- `gold__country_rise_potential`
- `gold__country_trajectory_momentum`
- `gold__trajectory_country_quadrant`
- `gold__trajectory_global_year`
- `gold__trajectory_component_breakdown`

## High-level architecture

```text
Raw Sources
  -> Bronze ingestion tables
  -> Silver standardized country-year facts
  -> Gold feature marts
  -> Gold analytical scoring models
  -> Validation SQL and dashboard-ready outputs
```

## Main datasets used

- World Bank WDI
- UN Population Division / WPP
- WHO-linked health indicators
- V-Dem governance indicators
- ND-GAIN climate indicators
- UCDP conflict indicators
- WID inequality indicators
- HDI / UNDP-related development indicators

## Time coverage

- Historical analytical window: 1950-2023 for broad features
- Trajectory scoring window: 1995-2023 historical observed
- Forecast extension: 2024-2045 baseline scenario

## Forecast interpretation

The 2024-2045 scenario is a **baseline continuation scenario**.

Projected inputs are directly available for:

- population
- life expectancy
- GDP / GDP per capita

For variables without direct projections, the baseline scenario carries forward the latest available historical values for:

- governance
- adaptation readiness
- climate vulnerability
- conflict severity

This means forecast outputs should be read as **structured continuation paths**, not as full causal forecasts of politics, climate shocks, or war.

**Main findings at a glance**

- Europe remains the strongest overall structural region by 2045.
- Asia is the most heterogeneous region, with countries across all trajectory categories.
- Africa remains the most concentrated in structural-risk outcomes under the baseline scenario.
- Guyana emerges as the most prominent high-momentum outlier.
- Global convergence appears limited; structural hierarchy persists into 2045.

---

## How to run the project

1. Environment setup

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

2. dbt setup

```bash
dbt deps
```

3. Build models

```bash
dbt run
```

4. Run tests

```bash
dbt test
```

**Suggested usage flow**

1. Build bronze and silver layers.
2. Build `gold__mart_world2045_features_country_year`.
3. Build forecast feature model.
4. Build trajectory scenario model.
5. Build rise-potential, momentum, and quadrant models.
6. Run validation SQL in the training manual.
7. Use the dashboard-ready marts for visualization.

# Live Dashboard

Streamlit dashboard deployed on Hugging Face:

https://sofian75-world2045-dashboard.hf.space

## Quick Start

1. Clone the repository:

```bash
git clone https://github.com/<username>/dsai-m2-personal-assignment.git
cd dsai-m2-personal-assignment
```

2. Create virtual environment

```
python -m venv .venv
source .venv/bin/activate
```

3. Install dependencies

```
pip install -r requirements.txt
```

4. Run the Streamlit dashboard locally

```
streamlit run dashboard/app/app.py
```

## Intended audiences (external)

- United Nations
- Geopolitical Groups
- Nation-state Governments
- Special Interest Groups

## Intended audiences (coursework)

- instructors and reviewers who need project traceability
- data engineers who need reproducible warehouse design
- data analysts who need country-year analytical tables
- learners who want to understand why each analytical layer exists

---

# Running the Local Analysis Notebook

This repository includes a **self-contained DuckDB notebook
environment** that allows users to run the analytical SQL queries
locally without requiring access to the BigQuery warehouse.

The notebook operates on a **curated sample dataset** exported from the
project's BigQuery gold marts.

## Repository structure required

    data/sample/
        <table_name>/
            *.parquet

Example:

    data/sample/gold__country_rise_potential/*.parquet
    data/sample/gold__region_trajectory_score_year/*.parquet

Each folder corresponds to a table. The notebook automatically loads
these tables into DuckDB.

------------------------------------------------------------------------

## Quick Start (3 Commands)

Clone the repository:

    git clone https://github.com/<your-org>/<repo-name>.git
    cd <repo-name>

Create and activate a Python environment:

    python -m venv .venv
    source .venv/bin/activate

Install required packages:

    pip install duckdb pandas jupyter

Launch Jupyter:

    jupyter notebook

Open the notebook:

    main/notebook/WORLD2045_Training_Manual_Data_Analyst.ipynb

Run the cells from top to bottom.

**1. What happens in the setup cell**

The notebook automatically:

1.  Locates the `data/sample` directory.
2.  Loads all Parquet folders as DuckDB tables.
3.  Enables optimized execution settings.

Example configuration executed during setup:

``` python
con.execute("PRAGMA threads=4")
con.execute("PRAGMA enable_progress_bar")
```

**2. Inspecting loaded table**

The notebook includes helper functions for exploring the dataset.

List all tables:

``` python
show_tables()
```

Inspect schema:

``` python
describe_table("gold__country_rise_potential")
```

Run SQL queries:

``` python
run_query("""
SELECT *
FROM gold__country_rise_potential
LIMIT 10
""")
```

**3. Dataset notes**

The dataset included in `data/sample/` is a **curated subset** of the
full World2045 warehouse.

It is intended for:

-   demonstration
-   reproducibility
-   local notebook execution

Results produced from the sample dataset may differ from the full
warehouse analysis.

For authoritative results, queries should be executed against the
BigQuery warehouse.

------------------------------------------------------------------------

## Local Analytical Notebook Architecture

The analytical notebook is designed to run **entirely offline** using a
curated subset of the project's analytical warehouse tables.

The workflow extracts a subset of the BigQuery gold marts and converts
them into Parquet files that can be queried locally using DuckDB.

## Architecture overview

    BigQuery Warehouse
            │
            ▼
    Filtered EXPORT DATA
            │
            ▼
    Parquet dataset (data/sample)
            │
            ▼
    DuckDB local query engine
            │
            ▼
    Jupyter analytical notebook

------------------------------------------------------------------------

## Step-by-step workflow

**1. BigQuery analytical warehouse**

Primary analytical data is stored in **BigQuery gold marts** generated
via dbt models.

Examples:

    gold__country_rise_potential
    gold__country_trajectory_momentum
    gold__region_trajectory_score_year
    gold__subregion_trajectory_score_year

**2. Curated dataset export**

A filtered subset of the warehouse is exported using BigQuery
`EXPORT DATA` statements.

Example:

    EXPORT DATA OPTIONS(
      uri='gs://bucket/world2045_sample/<table>/*.parquet',
      format='PARQUET'
    )
    AS SELECT * FROM world2045_ci.<table>;

**3. Local Parquet dataset**

Exported tables are stored locally:

    data/sample/
        <table_name>/
            *.parquet

**4. DuckDB local query engine**

The notebook registers the Parquet files as DuckDB views so they can be
queried using SQL.

Example:

    CREATE VIEW gold__country_rise_potential AS
    SELECT * FROM read_parquet('data/sample/gold__country_rise_potential/*.parquet')

**5. Jupyter analytical notebook**

Queries are executed using the `run_query()` helper.

Example:

    run_query("""
    SELECT
        country_name,
        trajectory_score_2023,
        trajectory_score_2045
    FROM gold__country_rise_potential
    ORDER BY trajectory_score_2045 DESC
    LIMIT 10
    """)

------------------------------------------------------------------------

## Project Structure (notebook section)

Below is the simplified structure of the repository (notebook section).

    dsai-m2-personal-assignment/
    │
    ├─ main/
    │   └─ notebook/
    │       └─ WORLD2045_Training_Manual_Data_Analyst.ipynb
    │
    ├─ data/
    │   └─ sample/
    │       ├─ country_overrides/
    │       ├─ dim__country/
    │       ├─ gold__country_rise_potential/
    │       ├─ gold__country_trajectory_momentum/
    │       ├─ gold__country_trajectory_score_year_scenario/
    │       ├─ gold__features_world2045_normalized_country_year/
    │       ├─ gold__forecast_feature_country_year/
    │       ├─ gold__mart_world2045_features_analytic_1960_2023/
    │       ├─ gold__mart_world2045_features_country_year/
    │       ├─ gold__region_trajectory_score_year/
    │       ├─ gold__subregion_trajectory_score_year/
    │       └─ gold__trajectory_country_quadrant/
    │
    ├─ dbt/
    │   └─ models/
    │
    ├─ dashboard/
    │
    ├─ scripts/
    │
    └─ README.md

This layout separates:

-   **data engineering pipelines** (dbt models)
-   **analysis environments** (notebooks)
-   **sample datasets** for reproducible local execution.

------------------------------------------------------------------------

## Reproducibility

Because the notebook operates on a static Parquet dataset, anyone
cloning the repository can reproduce the analysis locally without
requiring:

-   Google Cloud credentials
-   BigQuery access
-   dbt execution

---

# Acknowledgements

Portions of the technical design, debugging support, and documentation refinement for this project were assisted by **ChatGPT (OpenAI)**. All final implementation decisions, data engineering work, analytical modeling, and system integration were performed by the project author.
