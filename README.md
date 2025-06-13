# Hotel Data Utilities

This package contains utilities for working with [a GeoPackage file containing hotel (and other lodging) stay data](docs/data_structure.md).

For all of the below scripts, the location on any given day is considered to be where the traveler woke up the morning of that day.

## Nights, Mornings, and Evenings

Hotel stays are measured (and billed) by nights rather than days. A one-night stay generally involves two separate calendar days (check in on one day and check out the next). Likewise, longer stays involve one more day than nights; for example, a four-night stay involves five calendar days.

![Five calendar days, with check in on the first day and check out on the fifth day. Four nights span the four boundaries between the five calendar days, labeled night 0 through night 3. The first day contains check in and evening 0. The second day contains morning 0 and evening 1. The third day contains morning 1 and evening 2. The fourth day contains morning 2 and evening 3. The fifth day contains morning 3 and check out.](docs/images/nights-calendar-v4.svg)

Each night at a hotel spans two calendar days. For any given stay, the dates of morning[*n*] and evening[*n+1*] are the same. The check in date is always equal to evening[0], and the check out date is always equal to the last morning.

When scripts in this project need to assign a single specific date to each night, the morning date is used.

> [!NOTE]
> For some hotel stays, the check-in may occur after midnight (or the check out may occur before midnight). In these instances, a hotel night will only actually involve one single calendar day. However, since the reservation would still cover both calendar days, the night’s evening will still be recorded as the day prior to the night’s morning.

## Scripts

### Distance from Home by Day

[distance_from_home_by_day.py](distance_from_home_by_day.py)

This script generates a Matplotlib chart showing every calendar day (from 1 Jan to 31 Dec) on the X axis, and distance from home on the Y axis. Can also be used to show multiple years at once, as well as an average distance from home for each calendar day.

### Frequency Table

[frequency_table.py](frequency_table.py)

This script generates a Pandas DataFrame with each row containing a *Location*, *Type* (location, city, region, or metro), *Latitude*, *Longitude*, and *Nights* (count of nights). This can be exported to CSV for use in GIS software.

### Nights Away and Home

[nights_away_and_home.py](nights_away_and_home.py)

This script generates an SVG image for a plot of nights spent traveling (divided into work and personal nights) and nights spent at home.

## Data Structure

These scripts depend on lodging data structured in GeoPackage with a particular format, as documented in [Data Structure](docs/data_structure.md).