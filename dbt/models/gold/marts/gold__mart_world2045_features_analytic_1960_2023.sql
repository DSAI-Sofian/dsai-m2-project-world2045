{{ config(
    materialized = 'view'
) }}

select *
from {{ ref('gold__mart_world2045_features_country_year') }}
where year between 1960 and 2023