# WORLD IN 2045

'World in 2045' is a country-year data engineering and analytics project that studies long-run development patterns from 1950 to 2045. It integrates population, economic, health, governance, climate, conflict, inequality, and human-development indicators into a unified BigQuery + dbt analytical platform.

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

## Main findings at a glance

- Europe remains the strongest overall structural region by 2045.
- Asia is the most heterogeneous region, with countries across all trajectory categories.
- Africa remains the most concentrated in structural-risk outcomes under the baseline scenario.
- Guyana emerges as the most prominent high-momentum outlier.
- Global convergence appears limited; structural hierarchy persists into 2045.

## How to run the project

### Environment setup

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### dbt setup

```bash
dbt deps
```

### Build models

```bash
dbt run
```

### Run tests

```bash
dbt test
```

## Suggested usage flow

1. Build bronze and silver layers.
2. Build `gold__mart_world2045_features_country_year`.
3. Build forecast feature model.
4. Build trajectory scenario model.
5. Build rise-potential, momentum, and quadrant models.
6. Run validation SQL in the training manual.
7. Use the dashboard-ready marts for visualization.

## Live Dashboard

Streamlit dashboard deployed on Hugging Face:

https://sofian75-world2045-dashboard.hf.space

### Quick Start

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

## Acknowledgements

Portions of the technical design, debugging support, and documentation refinement for this project were assisted by **ChatGPT (OpenAI)**. All final implementation decisions, data engineering work, analytical modeling, and system integration were performed by the project author.
