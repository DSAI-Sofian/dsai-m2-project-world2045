{{ config(
    materialized = 'table'
) }}

with source_features as (

    select
        country_iso3,
        year,
        hdi,
        gini_income,
        bottom50_income_share_pct,
        top10_income_share_pct,
        top1_income_share_pct
    from {{ ref('gold__mart_world2045_features_country_year') }}

),

direction_aligned as (

    select
        country_iso3,
        year,

        hdi as hdi_aligned,
        -1 * gini_income as gini_income_aligned,
        bottom50_income_share_pct as bottom50_income_share_pct_aligned,
        -1 * top10_income_share_pct as top10_income_share_pct_aligned,
        -1 * top1_income_share_pct as top1_income_share_pct_aligned

    from source_features

),

stats as (

    select
        avg(hdi_aligned) as mean_hdi,
        stddev_pop(hdi_aligned) as std_hdi,

        avg(gini_income_aligned) as mean_gini_income,
        stddev_pop(gini_income_aligned) as std_gini_income,

        avg(bottom50_income_share_pct_aligned) as mean_bottom50_income_share_pct,
        stddev_pop(bottom50_income_share_pct_aligned) as std_bottom50_income_share_pct,

        avg(top10_income_share_pct_aligned) as mean_top10_income_share_pct,
        stddev_pop(top10_income_share_pct_aligned) as std_top10_income_share_pct,

        avg(top1_income_share_pct_aligned) as mean_top1_income_share_pct,
        stddev_pop(top1_income_share_pct_aligned) as std_top1_income_share_pct

    from direction_aligned

)

select
    sf.country_iso3,
    sf.year,

    sf.hdi,
    sf.gini_income,
    sf.bottom50_income_share_pct,
    sf.top10_income_share_pct,
    sf.top1_income_share_pct,

    da.hdi_aligned,
    da.gini_income_aligned,
    da.bottom50_income_share_pct_aligned,
    da.top10_income_share_pct_aligned,
    da.top1_income_share_pct_aligned,

    case
        when st.std_hdi is null or st.std_hdi = 0 or da.hdi_aligned is null then null
        else (da.hdi_aligned - st.mean_hdi) / st.std_hdi
    end as hdi_zscore,

    case
        when st.std_gini_income is null or st.std_gini_income = 0 or da.gini_income_aligned is null then null
        else (da.gini_income_aligned - st.mean_gini_income) / st.std_gini_income
    end as gini_income_zscore,

    case
        when st.std_bottom50_income_share_pct is null or st.std_bottom50_income_share_pct = 0 or da.bottom50_income_share_pct_aligned is null then null
        else (da.bottom50_income_share_pct_aligned - st.mean_bottom50_income_share_pct) / st.std_bottom50_income_share_pct
    end as bottom50_income_share_pct_zscore,

    case
        when st.std_top10_income_share_pct is null or st.std_top10_income_share_pct = 0 or da.top10_income_share_pct_aligned is null then null
        else (da.top10_income_share_pct_aligned - st.mean_top10_income_share_pct) / st.std_top10_income_share_pct
    end as top10_income_share_pct_zscore,

    case
        when st.std_top1_income_share_pct is null or st.std_top1_income_share_pct = 0 or da.top1_income_share_pct_aligned is null then null
        else (da.top1_income_share_pct_aligned - st.mean_top1_income_share_pct) / st.std_top1_income_share_pct
    end as top1_income_share_pct_zscore

from source_features sf
left join direction_aligned da
    on sf.country_iso3 = da.country_iso3
   and sf.year = da.year
cross join stats st