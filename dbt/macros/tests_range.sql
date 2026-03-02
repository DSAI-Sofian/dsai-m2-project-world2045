{% test accepted_range(model, column_name, min_value=None, max_value=None) %}

WITH base AS (
  SELECT {{ column_name }} AS v
  FROM {{ model }}
  WHERE {{ column_name }} IS NOT NULL
)
SELECT *
FROM base
WHERE
  {% if min_value is not none %} v < {{ min_value }} {% else %} FALSE {% endif %}
  OR
  {% if max_value is not none %} v > {{ max_value }} {% else %} FALSE {% endif %}

{% endtest %}