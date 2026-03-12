# Technical Architecture

Data Platform Stack

BigQuery warehouse  
dbt transformation layer  
Python ingestion scripts  
Country-year spine model

Core Models

fact_country_year_spine  
silver__fact_population_country_year  
silver__fact_hdi_country_year  
silver__fact_hdi_country_year_annualized  

Gold Layer

gold__mart_world2045_features_country_year

Normalized Layer

gold__features_world2045_normalized_country_year

Model Dataset

gold__mart_world2045_model_dataset
