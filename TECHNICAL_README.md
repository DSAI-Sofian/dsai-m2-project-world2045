# Technical README

## Environment Setup

Python virtual environment

python -m venv .venv
source .venv/bin/activate

Install dbt

pip install "dbt-core==1.11.*" "dbt-bigquery==1.11.*"

## dbt Profiles

profiles.yml must contain profile:

world2045

Dataset controlled via environment variable:

export DBT_DATASET=world2045_ci

## BigQuery Dataset

Dataset location: US

Dataset:
world2045_ci

## Naming Conventions

Table naming pattern:

layer__entity

Examples:

silver__fact_population_country_year
gold__mart_world2045_features_country_year

## Partition Strategy

Large fact tables partitioned by:

year

Clustered by:

country_iso3

## Canonical Keys

country_iso3
year

## Current dbt Models

dim_country
dim_year
fact_country_year_spine
fact_population_country_year

## Known Fixes Applied

Resolved double-prefix naming caused by generate_alias_name macro.