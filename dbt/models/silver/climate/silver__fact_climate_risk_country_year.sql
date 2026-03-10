select
    country_iso3,
    cast(year as int64) as year,
    cast(ndgain_index as float64) as ndgain_index,
    cast(climate_vulnerability as float64) as climate_vulnerability,
    cast(adaptation_readiness as float64) as adaptation_readiness
from {{ source('bronze', 'nd_gain_country_year') }}
where country_iso3 is not null
  and year is not null