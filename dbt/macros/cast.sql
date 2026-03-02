{% macro safe_float(expr) -%}
  SAFE_CAST({{ expr }} AS FLOAT64)
{%- endmacro %}

{% macro safe_int(expr) -%}
  SAFE_CAST({{ expr }} AS INT64)
{%- endmacro %}

{% macro norm_iso3(expr) -%}
  UPPER(TRIM({{ expr }}))
{%- endmacro %}