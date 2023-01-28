# Hotel Data Utilities

This package contains utilities for working with an [Excel spreadsheet of hotel stay data](#hotel-data-format).

For all of the below scripts, the location on any given day is considered to be where the traveler woke up the morning of that day.

## Utilities

### Distance from Home by Day

[distance_from_home_by_day.py](distance_from_home_by_day.py)

This script generates an SVG XY scatter chart showing every calendar day (from 1 Jan to 31 Dec) on the X axis, and distance from home on the Y axis, with points colored by year. An average distance from home for each day is also shown.

### Location Frequency Map Data

[location_frequency_map_data.py](location_frequency_map_data.py)

This script generates a CSV file with each row containing a `City`, `Latitude`, `Longitude`, and `Frequency` (count of nights). This can be used to generate a heatmap in GIS software by plotting a point for each date.

### Nights Away and Home

[nights_away_and_home.py](nights_away_and_home.py)

This script generates an SVG image for a plot of nights spent traveling (divided into work and personal nights) and nights spent at home.

For this script to work, the [hotel data](#hotel-data-format) must also have a `Purpose` column with values of either `Business` or `Personal` for each stay.

## Hotel Data Format

The hotel data should be in an Excel spreadsheet, with a sheet title of `Hotel Data`. The data should contain a row for each hotel stay, in a titled table with at least the following columns:

* The `Checkout Date` of the hotel stay
* The number of `Nights` spent at the hotel during this stay
* The `City` where the hotel is located, as described in City Format below

Some scripts may require additional columns.

### City Format

City names should be formed of the following, in order:

- [ISO 3166 Alpha-2](https://www.iso.org/obp/ui/#search) country code
- Subdivision part of [ISO 3166-2](https://en.wikipedia.org/wiki/ISO_3166-2) subdivision code (if applicable)
- City name (capital A-Z and spaces only). US cities should use [USPS city name](https://tools.usps.com/zip-code-lookup.htm) if available.

All of the above should be separated by forward slashes. For example:

- `AU/NSW/SYDNEY`
- `IS/REYKJAVIK`
- `US/MO/SAINT LOUIS`
- `US/NC/WINSTON SALEM`

### Overnight Flights

A traveler may wake up the morning of a particular day on an overnight flight.

In most cases, the location of a red-eye flight should be the airport where the flight arrives. Such a location should be recorded as `FLIGHT`, a forward slash, and the arrival IATA code (`FLIGHT/KEF`).

In certain situations, an overnight flight may last longer than a calendar day, such as some westbound flights across the International Date Line that land two calendar days after they depart. For example, consider a flight that departs DFW on 10 Feb (Dallas time) and lands in SYD on 12 Feb (Sydney time). The traveler’s location on the morning of 11 Feb should be recorded as the midpoint of the flight, represented as `FLIGHT`, a forward slash, and the IATA code of both airports separated by a hyphen (`FLIGHT/DFW-SYD`). The location for the morning of 12 February should be recorded as the arrival airport only (`FLIGHT/SYD`).

## Database Format

Some of these scripts require an SQLite database of location data, whose location should be set in `config.toml`. It should have three tables: `cities`, `metro_areas`, and `us_states`. At a minimum, every city listed in the hotel spreadsheet should have an entry in the `cities` table.

### cities

- `city_id` (TEXT): A unique identifier for each city as described in [City Format](#city-format) above
- `name` (TEXT): The city’s name
- `latitude` (REAL): Latitude of the city in decimal degrees
- `longitude` (REAL): Longitude of the city in decimal degrees
- `metro_id` (TEXT): The id of the city’s metro area (as defined in the `metro_areas` table), or null if the city is not in a metro area

### metro_areas

- `metro_id` (TEXT): A unique identifier for the metro area. Should always start with the ISO A2 country code and a slash, and typically then follows the city ID format for the metro area’s main city (`IS/REYKJAVIK`). However, if the country has its own ID scheme for metro areas, use that instead of a city name (`US/35620`).
- `metro_title` (TEXT): The official name of the metro area, or the city name of the primary city if an official name is not available
- `short_name` (TEXT): The name of the primary city of the metro area
- `latitude` (REAL): Latitude of the metro in decimal degrees
- `longitude` (REAL): Longitude of the metro in decimal degrees

### us_states

- `abbrev` (TEXT): Two-letter postal code for the state
- `name` (TEXT): Name of the state
- `latitude` (REAL): Latitude of the state in decimal degrees
- `longitude` (REAL): Longitude of the state in decimal degrees