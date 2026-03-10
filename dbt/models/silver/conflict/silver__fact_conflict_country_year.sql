select
    country_iso3,
    cast(year as int64) as year,
    cast(battle_deaths as float64) as battle_deaths,
    cast(conflict_incidence as int64) as conflict_incidence,
    cast(interstate_conflict as int64) as interstate_conflict,
    cast(civil_conflict as int64) as civil_conflict,
    cast(internationalized_conflict as int64) as internationalized_conflict,
    cast(war_intensity as int64) as war_intensity
from {{ source('bronze', 'ucdp_conflict_country_year') }}
where country_iso3 is not null
  and year is not null