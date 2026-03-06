# Technical README – World in 2045 Data Platform

## Architecture

The platform follows a layered architecture:

Bronze → Silver → Gold

Bronze: raw ingestion  
Silver: conformed warehouse models  
Gold: analytical marts

---

# Data Warehouse

Platform uses Google BigQuery.

Dataset:

world2045_ci

---

# dbt Structure

models/

bronze/  
silver/  
  dims/  
  facts/  
gold/

seeds/

country_overrides.csv

---

# Python Ingestion Framework

src/world2045/

Modules:

ingest/wpp.py  
ingest/wdi.py

utils/io.py

---

# Scripts

run_bronze.py

Runs ingestion pipelines.

load_bronze_bigquery.py

Loads CSV outputs to BigQuery tables.

---

# Development Workflow

Run ingestion:

python scripts/run_bronze.py

Load to BigQuery:

python scripts/load_bronze_bigquery.py

Build warehouse:

cd dbt
dbt build

---

# Testing

dbt tests validate:

primary keys  
not-null columns  
relationships

---

# Future Extensions

Planned datasets:

V‑Dem governance indicators  
Climate datasets  
Education metrics  
Conflict datasets

All future datasets attach to:

fact_country_year_spine