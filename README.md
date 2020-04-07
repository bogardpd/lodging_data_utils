# Hotel Data Utilities

This package contains utilities for working with an Excel spreadsheet of hotel stay data.

## Utilities

### distance_from_home_by_day.py

This script parses hotel stay data from an Excel spreadsheet, and generates an SVG XY scatter chart showing every calendar day (from 1 Jan to 31 Dec) on the X axis, and distance from home on the Y axis, with points colored by year. An average distance from home for each day is also shown.

### heatmap_data.py

This script parses hotel stay data, and generates a CSV file with each row containing a `Date`, `Latitude`, and `Longitude`. This can be used to generate a heatmap in GIS software by plotting a point for each date.

## Hotel Data Format

The hotel data should be in an Excel spreadsheet, with a sheet title of `Hotel Data`. The data should contain a row for each hotel stay, in a titled table with at least the following columns:

* The `Checkout Date` of the hotel stay
* The number of `Nights` spent at the hotel during this stay
* The `City` where the hotel is located

`City` should be a string containing the country code, subdivision codes (if needed), and city name separated by forward slashes. These should match the structure of the data in `data/coordinates.json`. For example, Los Angeles would be stored as `US/CA/Los Angeles`.