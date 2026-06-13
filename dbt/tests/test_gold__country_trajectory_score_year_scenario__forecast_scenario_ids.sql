with invalid_rows as (

    select
        country_iso3,
        year,
        scenario_id
    from {{ ref('gold__country_trajectory_score_year_scenario') }}
    where is_forecast_year = true
      and scenario_id not in ('baseline_static_risk', 'baseline_ml_dynamic_risk')

)

select *
from invalid_rows
