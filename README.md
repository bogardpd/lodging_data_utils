# Hotel Data Utilities

This package contains utilities for working with an Excel spreadsheet of hotel stay data.

## Utilities

### distance_from_home_by_day.py

This script parses hotel stay data from an Excel spreadsheet, and generates an SVG XY scatter chart showing every calendar day (from 1 Jan to 31 Dec) on the X axis, and distance from home on the Y axis, with points colored by year. An average distance from home for each day is also shown.

## Hotel Data Format

The hotel data should be in an Excel spreadsheet, with a sheet title of `Hotel Data`. The data should contain a row for each hotel stay, in a titled table with at least the following columns:

* The `Checkout Date` of the hotel stay
* The number of `Nights` spent at the hotel during this stay
* The `City` where the hotel is located

`City` should be a string containing the country code, subdivision codes (if needed), and city name separated by forward slashes. These should match the structure of the data in `data/coordinates.json`. For example, Los Angeles would be stored as `US/CA/Los Angeles`.