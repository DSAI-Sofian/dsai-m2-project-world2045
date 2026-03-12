{{ config(
    materialized = 'table'
) }}

with normalized as (

    select
        country_iso3,
        year,
        hdi_zscore,
        gini_income_zscore,
        bottom50_income_share_pct_zscore,
        top10_income_share_pct_zscore,
        top1_income_share_pct_zscore
    from {{ ref('gold__features_world2045_normalized_country_year') }}

),

feature_mart as (

    select
        country_iso3,
        year,
        hdi,
        hdi_is_observed,
        hdi_is_interpolated
    from {{ ref('gold__mart_world2045_features_country_year') }}

),

assembled as (

    select
        n.country_iso3,
        n.year,

        n.hdi_zscore,
        n.gini_income_zscore,
        n.bottom50_income_share_pct_zscore,
        n.top10_income_share_pct_zscore,
        n.top1_income_share_pct_zscore,

        f.hdi,
        f.hdi_is_observed,
        f.hdi_is_interpolated,

        (
            case when n.hdi_zscore is not null then 1 else 0 end +
            case when n.gini_income_zscore is not null then 1 else 0 end +
            case when n.bottom50_income_share_pct_zscore is not null then 1 else 0 end +
            case when n.top10_income_share_pct_zscore is not null then 1 else 0 end +
            case when n.top1_income_share_pct_zscore is not null then 1 else 0 end
        ) as non_null_feature_count

    from normalized n
    left join feature_mart f
        on n.country_iso3 = f.country_iso3
       and n.year = f.year

),

final as (

    select
        country_iso3,
        year,

        hdi_zscore,
        gini_income_zscore,
        bottom50_income_share_pct_zscore,
        top10_income_share_pct_zscore,
        top1_income_share_pct_zscore,

        hdi,
        hdi_is_observed,
        hdi_is_interpolated,

        non_null_feature_count,

        non_null_feature_count >= 4 as is_model_usable,

        case
            when year between 1990 and 2023
             and non_null_feature_count >= 4 then true
            else false
        end as is_training_usable,

        case
            when year between 2024 and 2045
             and non_null_feature_count >= 4 then true
            else false
        end as is_scoring_usable,

        case
            when year between 1990 and 2023 then 'train_observed_period'
            when year between 2024 and 2045 then 'forecast_period'
            else 'pre_hdi_period'
        end as panel_period

    from assembled

)

select *
from final