{% macro generate_schema_name(custom_schema_name, node) -%}
  {# Single-dataset convention controlled by DBT_DATASET; fallback to target.dataset #}
  {{ env_var('DBT_DATASET', target.dataset) }}
{%- endmacro %}


{% macro generate_alias_name(custom_alias_name, node) -%}
  {# If the user set an explicit alias in config, respect it #}
  {% if custom_alias_name is not none %}
    {{ custom_alias_name }}
  {% else %}
    {# Prefix based on model folder (logical layer), but avoid double-prefixing #}
    {% set name = node.name %}

    {% if node.path.startswith('silver/') %}
      {% if name.startswith('silver__') %}
        {{ name }}
      {% else %}
        {{ 'silver__' ~ name }}
      {% endif %}

    {% elif node.path.startswith('gold/') %}
      {% if name.startswith('gold__') %}
        {{ name }}
      {% else %}
        {{ 'gold__' ~ name }}
      {% endif %}

    {% else %}
      {{ name }}
    {% endif %}
  {% endif %}
{%- endmacro %}