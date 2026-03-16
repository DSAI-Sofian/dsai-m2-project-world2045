# World in 2045 Streamlit + Hugging Face Deployment Guide

## Recommended deployment choice
Use **Hugging Face Spaces with Docker**, not the old built-in Streamlit SDK. Hugging Face officially states that the built-in Streamlit SDK is deprecated and that Streamlit apps should now be deployed via the Docker SDK.

## Local build order
1. Export small precomputed datasets from BigQuery/dbt gold models.
2. Save them into the `data/` folder as parquet or CSV.
3. Run locally with:
   ```bash
   pip install -r requirements.txt
   streamlit run app/app.py
   ```
4. Validate all six pages.
5. Push the repository to Hugging Face Space.

## Suggested extract files
- `global_year.parquet`
- `region_year.parquet`
- `country_scores.parquet`
- `country_components.parquet`
- `quadrants.parquet`
- `rankings.parquet`
- `doomsday_clock.csv`

## Hugging Face Space steps
1. Create a new Space.
2. Choose **Docker** as the SDK.
3. Name it something like `world2045-dashboard`.
4. Upload or push these files:
   - `Dockerfile`
   - `README.md`
   - `requirements.txt`
   - `app/`
   - `data/`
   - `.streamlit/`
5. Wait for the build to complete.
6. Open the Space and verify page navigation and charts.

## Practical notes
- Keep the dataset small. The app is intended for academic demo performance, not warehouse-scale exploration.
- Do not connect live to BigQuery unless the module requires it.
- Keep expensive transforms out of Streamlit. Precompute in dbt or Python first.
- If charts feel slow, reduce columns and row counts in the exports.

## Submission advice
Freeze the app with a stable export snapshot near submission time. That prevents last-minute drift between your report, screenshots, and live demo.
