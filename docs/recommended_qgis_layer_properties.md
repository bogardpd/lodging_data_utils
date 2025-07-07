# Recommended QGIS Layer Properties

This document contains recommended settings within QGIS for each layer’s properties. Fields which use default values are not included unless necessary for clarity.

## stays

### Attributes Form

- `check_out_date`
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
| `stays` | MEDIUMINT (32 bit) | ` aggregate('STAYS_LAYER', 'count', "nights", "stay_location_fid"=attribute(@parent, 'fid'))` |
| `nights` | MEDIUMINT (32 bit) | ` aggregate('STAYS_LAYER', 'sum', "nights", "stay_location_fid"=attribute(@parent, 'fid'))` |
| `is_home` | BOOLEAN | ` aggregate('HOMES_LAYER', 'count', "fid", "stay_location_fid"=attribute(@parent, 'fid')) > 0` |

### Attributes Form

- `type`
  - Widget Type: `Value Map`

| Value       | Description |
|-------------|-------------|
| NULL        | NULL        |
| `Hotel`     | `Hotel`     |
| `STR`       | `STR`       |
| `Residence` | `Residence` |
| `Flight`    | `Flight`    |

- `city_fid`
  - Widget Type: `Value Relation`
    - Layer: `cities`
  	- Key column: `fid`
  	- Value column: `key`
  	- Order By: `Value`
  	- Allow NULL value: `True`
- `address`
  - Widget Type: `Text Edit`
    - Multiline: `True`
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
