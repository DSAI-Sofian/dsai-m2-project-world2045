# HDI Annualization Policy

The UNDP HDI trends dataset contains sparse anchor years only.

Observed HDI years:

1990  
2000  
2010  
2015  
2020  
2021  
2022  
2023  

To create a continuous analytical panel, HDI values are interpolated annually.

Rules:

Linear interpolation between anchor years  
No forward fill  
No backfill before 1990  
No extrapolation beyond 2023

Transparency fields:

hdi_is_observed  
hdi_is_interpolated
