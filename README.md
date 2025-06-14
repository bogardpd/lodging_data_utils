# Hotel Data Utilities

This package contains utilities for working with a traveler’s personal lodging log. In addition to hotel stays, this log can also document stays at short-term-rentals, stays with friends and family, and even overnight flights.

## Data Structure

These scripts use a GeoPackage (.gpkg) file as their primary data source. The structure of this file is documented in [Data Structure](docs/data_structure.md).

## Definitions: Nights, Mornings, and Evenings

Hotel stays are measured (and billed) by nights rather than days. A one-night stay generally involves two separate calendar days (check in on one day and check out the next). Likewise, longer stays involve one more day than nights; for example, a four-night stay involves five calendar days.

![Five calendar days, with check in on the first day and check out on the fifth day. Four nights span the four boundaries between the five calendar days, labeled night 0 through night 3. The first day contains check in and evening 0. The second day contains morning 0 and evening 1. The third day contains morning 1 and evening 2. The fourth day contains morning 2 and evening 3. The fifth day contains morning 3 and check out.](docs/images/nights-calendar-v4.svg)

Each night at a hotel spans two calendar days. For any given stay, the dates of morning[*n*] and evening[*n+1*] are the same. The check in date is always equal to evening[0], and the check out date is always equal to the last morning.

When scripts in this project need to assign a single specific date to each night, the morning date is used.

> [!NOTE]
> For some hotel stays, the check-in may occur after midnight (or the check out may occur before midnight). In these instances, a hotel night will only actually involve one single calendar day. However, since the reservation would still cover both calendar days, the night’s evening will still be recorded as the day prior to the night’s morning.

## Scripts

### Annual Night Counts

Generates a CSV file with the following columns:

| Column | Description |
|--------|-------------|
| year | Every year from the first morning of the earliest stay to the present |
| business_night_count | Number of nights away from home for business travel |
| personal_night_count | Number of nights away from home for personal travel |

#### Script

`annual_night_counts.py`

#### Arguments

- `output_file` (required): Path to the output CSV file.

#### Usage Example
```sh
python annual_night_counts.py output/annual_night_counts.csv
```

### Distance from Home by Day

Generates a Matplotlib chart showing every calendar day (from 1 Jan to 31 Dec) on the X axis, and distance from home on the Y axis. Can also be used to show multiple years at once, as well as an average distance from home for each calendar day.

![A sample distance from home by day chart for 2023](docs/images/distance-from-home-by-day-2023.svg)

In single year mode, the script can also produce a CSV output of distance data with the following columns:

| Column | Description |
|--------|-------------|
| title  | Year (YYYY) |
| dates  | Morning date (YYYY-MM-DD) |
| distances | Distance from home in miles (floating point)

#### Script

`distance_from_home_by_day.py`

#### Subcommands
- `single`: Plot for a single year.
- `multi`: Plot for a range of years and/or average.

#### Arguments for `single`

- `--year YYYY` (required): Year to plot.
- `--labels FILE` (optional): A CSV file with CheckOutDate and Location Columns, specifying dates to label.
- `--earliest_prior_year YYYY` (optional): Show prior years starting from this year for comparison.
- `--output FILE` (optional): Output image file path (SVG or PNG). If included, output CSV distance data will also be saved to the same path with a .csv extension (e.g. **path/output.png** → **path/output.csv**).

#### Arguments for `multi`

- `--start_year YYYY` (required): First year to include.
- `--end_year YYYY` (required): Last year to include.
- `--output FILE` (required): Output image file path(s) (SVG or PNG).

#### Usage Examples

- Single year:
    ```sh
    python distance_from_home_by_day.py single --year 2023 --output output/distance_2023.svg
    ```

- Single year with prior years for comparison:
    ```sh
    python distance_from_home_by_day.py single --year 2023 --earliest_prior_year 2019 --output output/distance_2023_with_prior.png
    ```

- Range of years with average:
    ```sh
    python distance_from_home_by_day.py multi --start_year 2019 --end_year 2023 --output output/distance_multi.svg
    ```

### Frequency Table

Generates a Pandas DataFrame of places, which groups all stays by a specified place level (stay location, city, region, or metro) and provides the total nights spent at each.

If a stay does not have the specified place level, the broadest level place that is available will be used. For example, if grouping by metro but a stay is in a city that’s not in a metro area, the city will be used instead.

The dataframe has the following structure:

| Column | Description |
|--------|-------------|
| Rank | The rank of this place. Only present when `--rank` is specified. | 
| Title  | Formal name of the place. Not used for stay location |
| Location | Short name for use in map labels |
| LocId | fid (stay locations), key (cities, metros), or ISO 3166-2 (regions)
| Type | **StayLocation**, **City**, **Metro**, or **Region**. Typically the location level specified by the `--by` argument. If some data does not have the specified level, then this column shows the level actually used.
| Latitude | Latitude in decimal degrees |
| Longitude | Longitude in decimal degrees |
| Nights | Number of nights spent at this place |

This can be exported to CSV for use in GIS software.

#### Script

`frequency_table.py`

#### Arguments
- `--by {location,city,region,metro}` (required): Grouping level.
- `--start YYYY-MM-DD` (optional): The earliest morning to include. If omitted, will use the earliest morning in the log data.
- `--thru YYYY-MM-DD` (optional): The latest morning to include. If omitted, will use today’s date.
- `--exclude_flights` (optional): Exclude nights spent in transit (flights).
- `--output FILE` (optional): Output CSV file path.
- `--top N` (optional): Show only the top N results.
- `--rank` (optional): Add a ranking column.
- `--silent` (optional): Do not show output table in the console.

#### Usage Examples

- Group by city and print to console:
    ```sh
    python frequency_table.py --by city
    ```

- Group by region, exclude flights, and save to CSV:
    ```sh
    python frequency_table.py --by region --exclude_flights --output output/frequency_by_region.csv
    ```

- Show top 10 locations, ranked:
    ```sh
    python frequency_table.py --by location --top 10 --rank
    ```

### Nights Away and Home

Generates an SVG image for a plot of nights spent traveling (divided into work and personal nights) and nights spent at home.

#### Script

`nights_away_and_home.py`

#### Arguments

- `--output FILE` (required): Output SVG image file path.
- `--stats_output FILE` (optional): Output text file for summary stats.
- `--start YYYY-MM-DD` (optional): The first evening to include in the chart. If omitted, will use the earliest evening in the log data.
- `--thru YYYY-MM-DD` (optional): The last morning to include in the chart. If omitted, will use today’s date.

#### Usage Examples

- Include a stats output file:
```sh
python nights_away_and_home.py --output output/nights_away_and_home.svg --stats_output output/nights_stats.txt
```

- Filter by a date range:
```sh
python nights_away_and_home.py --output output/nights_2022.svg --start 2022-01-01 --thru 2022-12-31
```
