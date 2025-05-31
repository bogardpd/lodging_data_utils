# Hotel Data Utilities

This package contains utilities for working with [hotel (and other lodging) stay data](docs/data_structure.md#lodging-data-format).

For all of the below scripts, the location on any given day is considered to be where the traveler woke up the morning of that day.

## Utilities

### Distance from Home by Day

[distance_from_home_by_day.py](distance_from_home_by_day.py)

This script generates a Matplotlib chart showing every calendar day (from 1 Jan to 31 Dec) on the X axis, and distance from home on the Y axis. Can also be used to show multiple years at once, as well as an average distance from home for each calendar day.

### Frequency Table

[frequency_table.py](frequency_table.py)

This script generates a Pandas DataFrame with each row containing a *Location*, *Type* (city, state, or metro), *Latitude*, *Longitude*, and *Nights* (count of nights). This can be exported to CSV for use in GIS software.

### Nights Away and Home

[nights_away_and_home.py](nights_away_and_home.py)

This script generates an SVG image for a plot of nights spent traveling (divided into work and personal nights) and nights spent at home.

## Data Structure

These scripts depend on lodging data structured in a particular format, as documented in [Data Structure](docs/data_structure.md).