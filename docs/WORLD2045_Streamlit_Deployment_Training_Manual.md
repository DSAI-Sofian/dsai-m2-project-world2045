# World2045 Streamlit Deployment Manual

This guide documents the complete process used to deploy the World2045 analytical dashboard using Streamlit and Hugging Face Spaces. It is written for learners who are new to Streamlit and provides step‑by‑step instructions including SQL validation queries, Python code, and Bash commands.

## 1. Project Context

The World2045 project builds a global development trajectory model using multiple datasets (population, GDP, governance, climate vulnerability, adaptation readiness, and conflict). The analytical pipeline follows a modern data architecture:
Bronze → Silver → Gold (dbt models on BigQuery). 
The Streamlit dashboard visualizes the final Gold analytical outputs.

## 2. Architecture Overview

Data Sources → BigQuery Warehouse → dbt Transformations → Gold Analytical Tables → CSV Extracts → Streamlit Dashboard → Hugging Face Deployment

## 3. Required Technologies

- Python 3.10+
- Streamlit
- Plotly
- Pandas
- Git
- WSL or Linux terminal
- Hugging Face account

## 4. Exporting Visualization Datasets

Export small precomputed extracts from the dbt Gold layer for dashboard use.

Example SQL: Global Trajectory Table

```
SELECT
year,
scenario_id,
is_forecast_year,
avg_trajectory_score,
country_count
FROM world2045_ci.gold__trajectory_global_year
ORDER BY year;
```

Example SQL: Regional Trajectory Table

```
SELECT 
region, 
year, 
scenario_id, 
avg_trajectory_score, 
country_count 
FROM world2045_ci.gold__region_trajectory_score_year; 
```

Example SQL: Country Scores

``` 
SELECT 
country_iso3, 
country_name, 
year, 
scenario_id, 
trajectory_score 
FROM world2045_ci.gold__country_trajectory_score_year_scenario 
WHERE is_rankable_forecast_case = TRUE; 
```

## 5. Exporting CSV Files

Save the exported query results as CSV files inside the dashboard/data folder:

- country_scores.csv
- country_components.csv
- region_year.csv
- global_year.csv
- quadrants.csv
- rankings.csv
- doomsday_clock.csv

## 6. Streamlit App Structure

```
dashboard/ 
├ app/ 
│  ├ app.py 
│  ├ pages/ 
│  │  ├ global_overview.py 
│  │  ├ country_explorer.py 
│  │  ├ regional_view.py 
│  │  ├ strategic_rankings.py 
│  │  ├ doomsday_clock.py 
│  │  └ methodology.py 
│  └ lib/ 
│     ├ loaders.py 
│     ├ charts.py 
│     └ ui.py 
└ data/ 
```

## 7. Running Streamlit Locally

Activate the Python virtual environment:

```
source .venv/bin/activate 
```

Launch the dashboard:
```
streamlit run app/app.py 
```

## 8. Common Debugging Commands

Check dataset structure:

```
head data/rankings.csv
```

Verify Guyana ranking row example:

```
grep Guyana data/rankings.csv
```

Clear Streamlit cache:

```
streamlit cache clear
```

Remove compiled Python cache files:

```
find app -type d -name '__pycache__' -exec rm -rf {} +
```

## 9. Hugging Face Deployment

Create a Hugging Face Space using the Streamlit template.

Clone the repository locally:

```
git clone https://huggingface.co/spaces/<username>/world2045-dashboard
```

Copy dashboard files into the Space repository.

Commit and push:

```
git add . 
git commit -m "Initial dashboard deployment" 
git push 
```

## 10. Verifying Deployment

After pushing, Hugging Face automatically builds the app.

Open the Space URL and test all pages:

- Global Overview loads charts
- Country Explorer shows trajectory and metrics
- Regional View displays regional trends
- Strategic Rankings tables render
- Doomsday Clock gauge shows ~70 seconds

## 11. Final Notes

The dashboard should use static CSV extracts from the analytical Gold tables. This ensures fast loading and reproducible results suitable for academic presentation.