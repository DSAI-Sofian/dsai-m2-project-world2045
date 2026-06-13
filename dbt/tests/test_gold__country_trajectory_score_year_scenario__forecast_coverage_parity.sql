with forecast as (

    select
        country_iso3,
        year,
        scenario_id
    from {{ ref('gold__country_trajectory_score_year_scenario') }}
    where is_forecast_year = true
      and scenario_id in ('baseline_static_risk', 'baseline_ml_dynamic_risk')

),

static_rows as (

    select country_iso3, year
    from forecast
    where scenario_id = 'baseline_static_risk'

),

ml_rows as (

    select country_iso3, year
    from forecast
    where scenario_id = 'baseline_ml_dynamic_risk'

),

missing_in_ml as (
    select
        s.country_iso3,
        s.year,
        'missing_in_ml_dynamic' as issue_type
    from static_rows s
    left join ml_rows m
      on s.country_iso3 = m.country_iso3
     and s.year = m.year
    where m.country_iso3 is null
),

missing_in_static as (
    select
        m.country_iso3,
        m.year,
        'missing_in_static' as issue_type
    from ml_rows m
    left join static_rows s
      on m.country_iso3 = s.country_iso3
     and m.year = s.year
    where s.country_iso3 is null
)

select * from missing_in_ml
union all
select * from missing_in_static
