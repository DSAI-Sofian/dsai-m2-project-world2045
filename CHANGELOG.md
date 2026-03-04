# CHANGELOG

## 2026-03-04

### Added
- WPP2024 ingestion workflow
- Bronze raw population table
- Bronze normalized population table
- Silver population fact model

### Fixed
- dbt profile misconfiguration
- GitHub CI YAML syntax errors
- dbt dependency installation issues
- BigQuery header incompatibility
- dbt alias macro double prefix bug

### Infrastructure
- BigQuery dataset configured
- dbt incremental merge strategy implemented
- Partitioning by year
- Clustering by country_iso3