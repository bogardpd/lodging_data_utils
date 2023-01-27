# Hotel Data Utilities

This package contains utilities for working with an [Excel spreadsheet of hotel stay data](#hotel-data-format).

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

- ISO 3166 A2 country code
- Subdivision part of ISO 3166-2 subdivision code (if applicable)
- City name (capital A-Z and spaces only). US cities should use [USPS city name](https://tools.usps.com/zip-code-lookup.htm) if available.

All of the above should be separated by forward slashes. For example:

- `AU/NSW/SYDNEY`
- `IS/REYKJAVIK`
- `US/MO/SAINT LOUIS`
- `US/NC/WINSTON SALEM`

Locations of overnight flights can also be included. If the location is to be the midpoint of a flight path, use `OVERNIGHT FLIGHT`, a forward slash, and the IATA code of both airports separated by a hyphen (`OVERNIGHT FLIGHT/DFW-SYD`). If only the arrival airport is to be used, use `OVERNIGHT FLIGHT`, a forward slash, and the arrival IATA code (`OVERNIGHT FLIGHT/KEF`).