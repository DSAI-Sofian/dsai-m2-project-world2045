{{ config(materialized='table') }}

with base as (

    select
        country_name,
        year,
        scenario_name,
        model_name,
        gdp_real_billion_usd
    from {{ ref('silver__stg_ssp_gdp_projection') }}

),

country_dim as (

    select distinct
        upper(trim(country_name)) as country_name_key,
        country_iso3
    from {{ ref('dim_country') }}
    where country_name is not null
      and country_iso3 is not null

    union distinct

    select distinct
        upper(trim(country_name_official)) as country_name_key,
        country_iso3
    from {{ ref('dim_country') }}
    where country_name_official is not null
      and country_iso3 is not null

),

country_overrides as (

    select distinct
        upper(trim(country_name)) as country_name_key,
        iso3 as country_iso3
    from {{ ref('country_overrides') }}
    where country_name is not null
      and iso3 is not null

    union distinct

    select distinct
        upper(trim(country_name_official)) as country_name_key,
        iso3 as country_iso3
    from {{ ref('country_overrides') }}
    where country_name_official is not null
      and iso3 is not null

),

manual_overrides as (

    select 'ANTIGUA AND BARBUDA' as country_name_key, 'ATG' as country_iso3 union all
    select 'ARUBA', 'ABW' union all
    select 'CURAÇAO', 'CUW' union all
    select 'DEMOCRATIC REPUBLIC OF THE CONGO', 'COD' union all
    select 'ESWATINI', 'SWZ' union all
    select 'FRENCH GUIANA', 'GUF' union all
    select 'FRENCH POLYNESIA', 'PYF' union all
    select 'GRENADA', 'GRD' union all
    select 'GUAM', 'GUM' union all
    select 'HONG KONG', 'HKG' union all
    select 'KIRIBATI', 'KIR' union all
    select 'KOSOVO', 'XKX' union all
    select 'MACAO', 'MAC' union all
    select 'MALDIVES', 'MDV' union all
    select 'MAYOTTE', 'MYT' union all
    select 'MICRONESIA', 'FSM' union all
    select 'MONTENEGRO', 'MNE' union all
    select 'NEW CALEDONIA', 'NCL' union all
    select 'NORTH KOREA', 'PRK' union all
    select 'NORTH MACEDONIA', 'MKD' union all
    select 'PAPUA NEW GUINEA', 'PNG' union all
    select 'PUERTO RICO', 'PRI' union all
    select 'SAINT LUCIA', 'LCA' union all
    select 'SAINT VINCENT AND THE GRENADINES', 'VCT' union all
    select 'SAMOA', 'WSM' union all
    select 'SAO TOME AND PRINCIPE', 'STP' union all
    select 'SEYCHELLES', 'SYC' union all
    select 'SOLOMON ISLANDS', 'SLB' union all
    select 'SOMALIA', 'SOM' union all
    select 'SOUTH SUDAN', 'SSD' union all
    select 'SURINAME', 'SUR' union all
    select 'TIMOR-LESTE', 'TLS' union all
    select 'TOGO', 'TGO' union all
    select 'TONGA', 'TON' union all
    select 'TRINIDAD AND TOBAGO', 'TTO' union all
    select 'TURKMENISTAN', 'TKM' union all
    select 'UNITED STATES VIRGIN ISLANDS', 'VIR' union all
    select 'VANUATU', 'VUT' union all
    select 'VIET NAM', 'VNM' union all
    select 'WESTERN SAHARA', 'ESH'

),

country_map as (

    select * from country_dim
    union distinct
    select * from country_overrides
    union distinct
    select * from manual_overrides

),

mapped as (

    select
        c.country_iso3,
        b.year,
        b.scenario_name,
        b.model_name,
        b.gdp_real_billion_usd
    from base b
    left join country_map c
      on upper(trim(b.country_name)) = c.country_name_key

)

select
    country_iso3,
    cast(year as int64) as year,
    scenario_name,
    model_name,
    cast(gdp_real_billion_usd as float64) as gdp_real_billion_usd
from mapped
where country_iso3 is not null
  and year is not null
  and scenario_name = 'SSP2'