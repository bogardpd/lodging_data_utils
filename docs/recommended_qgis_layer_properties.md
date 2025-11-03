# Recommended QGIS Layer Properties

This document contains recommended settings within QGIS for each layer’s properties. Fields which use default values are not included unless necessary for clarity.

## stays

### Attributes Form

- `check_in_date`
  - Widget Type: `Date/Time`
  - Defaults
    - Default value: `now()`
- `nights`
  - Widget Type: `Range`
    - Minimum: `1`
    - Maximum: `2147483647`
	- Allow NULL: `False`
- `portfolio`
  - Widget Type: `Unique Values`
    - Editable: `True`
- `brand`
  - Widget Type: `Unique Values`
    - Editable: `True`
- `stay_location_fid`
  - Widget Type: `Value Relation`
    - Layer: `stay_locations`
  	- Key column: `fid`
  	- Value column: `id_str`
  	- Order By: `Value`
  	- Allow NULL value: `False`
- `absence_flags`
  - Defaults
    - Default value: `NULL`

## homes

### Attributes Form

- `move_in_date`
  - Defaults
    - Default value: `now()`
- `stay_location_fid`
  - Widget Type: `Value Relation`
    - Layer: `stay_locations`
  	- Key column: `fid`
  	- Value column: `id_str`
  	- Order By: `Value`
  	- Allow NULL value: `False`

## stay_locations

### Virtual Fields

> [!NOTE]
> `CITIES_LAYER`, `STAYS_LAYER`, and `HOMES_LAYER` should be replaced with the appropriate Layer ID string.

| Name | Type | Expression |
|------|------|------------|
| `id_str` | TEXT | `if("city_fid", concat(attribute(get_feature_by_id('CITIES_LAYER', "city_fid"), 'key'), ':\n', "name"), "name")` |
| `stays` | MEDIUMINT (32 bit) | `coalesce(aggregate('STAYS_LAYER', 'sum', if("absence_flags" IS NULL, 1, if(length(replace("absence_flags", 'A', '')) > 0, 1, 0)), "stay_location_fid"=attribute(@parent, 'fid')), 0)` |
| `nights` | MEDIUMINT (32 bit) | `coalesce(aggregate('STAYS_LAYER', 'sum', "nights" - if("absence_flags" IS NULL, 0, length(replace("absence_flags", 'P', ''))), "stay_location_fid"=attribute(@parent, 'fid')), 0)` |
| `is_home` | BOOLEAN | `aggregate('HOMES_LAYER', 'count', "fid", "stay_location_fid"=attribute(@parent, 'fid')) > 0` |
| `stay_list` | TEXT | `aggregate(layer := 'STAYS_LAYER', aggregate := 'concatenate', expression := concat(format_date("check_in_date", 'yyyy-MM-dd'), ' (', "nights", if("nights" = 1, ' night)', ' nights)')), if("room" IS NOT NULL, concat(' rm. ', "room"), ''), filter := "stay_location_fid"=attribute(@parent, 'fid'), concatenator := '\n', order_by := "check_in_date")` |

### Attributes Form

- `type`
  - Widget Type: `Value Map`

| Value       | Description |
|-------------|-------------|
| NULL        | NULL        |
| `Hotel`     | `Hotel`     |
| `STR`       | `STR`       |
| `Campsite`  | `Campsite`  |
| `Residence` | `Residence` |
| `Flight`    | `Flight`    |
| `Other`     | `Other`     |

- `city_fid`
  - Widget Type: `Value Relation`
    - Layer: `cities`
  	- Key column: `fid`
  	- Value column: `key`
  	- Order By: `Value`
  	- Allow NULL value: `True`
- `brand`
  - Widget Type: `Unique Values`
    - Editable: `True`
- `portfolio`
  - Widget Type: `Unique Values`
    - Editable: `True`

## cities

### Attributes Form

- `key`
  - Constraints
    - Not null: `True`
    - Enforce not null constraint: `True`
    - Unique: `True`
    - Enforce unique constraint: `True`
- `metro_fid`
  - Widget Type: `Value Relation`
    - Layer: `metros`
  	- Key column: `fid`
  	- Value column: `id_str`
  	- Order By: `Value`
  	- Allow NULL value: `True`
- `region_fid`
  - Widget Type: `Value Relation`
    - Layer: `regions`
  	- Key column: `fid`
  	- Value column: `id_str`
  	- Order By: `Value`
  	- Allow NULL value: `False`

## metros

### Virtual Fields

| Name | Type | Expression |
|------|------|------------|
| `id_str` | TEXT | `concat("key", ':\n', if("title", "title", "name"))` |

### Attributes Form

- `key`
  - Constraints
    - Not null: `True`
    - Enforce not null constraint: `True`
    - Unique: `True`
    - Enforce unique constraint: `True`

## regions

### Virtual Fields

| Name | Type | Expression |
|------|------|------------|
| `id_str` | TEXT | `concat("iso_3166", ':\n', "name")` |

### Attributes Form

- `iso_3166`
  - Constraints
    - Not null: `True`
    - Enforce not null constraint: `True`
    - Unique: `True`
    - Enforce unique constraint: `True`
- `admin_level`
  - Widget Type: `Range`
    - Minimum: `0`
    - Maximum: `1`
    - Allow NULL: `False`
- `parent_region_fid`
  - Widget Type: `Value Relation`
    - Layer: `regions`
  	- Key column: `fid`
  	- Value column: `id_str`
  	- Order By: `Value`
  	- Allow NULL value: `True`
