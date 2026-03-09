
# World2045 dbt Indicator Mapping Table

| indicator_id | domain | source | model_column |
|---|---|---|---|
| POP_TOTAL | demography | WPP | population_total |
| POP_GROWTH | demography | WPP | population_growth_rate |
| MEDIAN_AGE | demography | WPP | median_age |
| FERTILITY_RATE | demography | WPP | fertility_rate |
| LIFE_EXPECTANCY | demography | WPP | life_expectancy |

| GDP_PER_CAPITA | economy | WDI | gdp_per_capita |
| GDP_GROWTH | economy | WDI | gdp_growth |
| INFLATION | economy | WDI | inflation |
| UNEMPLOYMENT | economy | WDI | unemployment |
| INVESTMENT_GDP | economy | WDI | investment_gdp |

| SECONDARY_ENROLLMENT | human_capital | WDI | secondary_enrollment |
| LITERACY_RATE | human_capital | WDI | literacy_rate |
| HEALTH_EXPENDITURE | human_capital | WDI | health_expenditure |
| INFANT_MORTALITY | human_capital | WDI | infant_mortality |
| PHYSICIANS_PER_1000 | human_capital | WHO/WDI | physicians_per_1000 |

| GINI | inequality | WDI | gini |
| POVERTY_RATE | inequality | WDI | poverty_rate |
| URBAN_POPULATION | inequality | WDI | urban_population |
| YOUTH_UNEMPLOYMENT | inequality | WDI | youth_unemployment |
| DEPENDENCY_RATIO | inequality | WDI | dependency_ratio |

| DEMOCRACY_INDEX | governance | VDEM | democracy_index |
| CORRUPTION_INDEX | governance | VDEM | corruption_index |
| POLITICAL_STABILITY | governance | WDI | political_stability |
| CONFLICT_DEATHS | conflict | ACLED | conflict_deaths |
| CLIMATE_VULNERABILITY | climate | NDGAIN | climate_vulnerability |
