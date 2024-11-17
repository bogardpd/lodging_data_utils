# Hotel Data Utilities

This package contains utilities for working with an [Excel spreadsheet of hotel (and other lodging) stay data](#lodging-data-format).

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

## Lodging Data

The lodging data should be in an Excel spreadsheet, with the following sheets:

### Stays

Information for each stay should be stored in a sheet titled *Stays*. The data should contain a row for each lodging stay, in a titled table with at least the following columns:

| Column | Format | Description |
|--------|--------|-------------|
| *CheckoutDate* | Date | The departure date from the stay (in the lodging location’s time zone), in **YYYY-MM-DD** format. If departure occurs prior to midnight but the stay is booked/billed through the following morning, then the following morning should be used as the checkout date. |
| *Nights* | Number (Integer) | The number of nights spent on the stay. Should be equal to the difference in days between the check-in date and the check-out date. |
| *FacilityId* | Number (Integer) | An optional identifier, tying the stay to a specific building or campus. May be used with an external geodata store to match stays to feature IDs. |
| *CityId* | Text | The city where the lodging is located, as described in [City Format](#city-format). |
| *MetroId* | Text | The metro where the lodging is located as of the CheckoutDate, as described in [Metro Format](#city-format). |
| *Type* | Text | **Hotel** (a hotel room), **STR** (Short Term Rental, such as Airbnb or VRBO), **Residence** (someone’s home), or **Flight** (as described in [Overnight Flights](#overnight-flights)).
| *Portfolio* | Text | A collection of hotel brands or short-term rentals, usually with its own loyalty program (e.g. **Hilton** or **VRBO**). Leave blank if this stay does not have a hotel portfolio. |
| *Brand* | Text | The brand of hotel (e.g. **Hampton Inn**). Short-term rentals will generally leave this blank. Hotels which are not part of a chain, residences, and overnight flights should leave this blank. |
| *Location* | Text | The name of the lodging. If the lodging is a chain hotel and the chain is part of the name, include the chain in the name (e.g. **Embassy Suites by Hilton Chicago Downtown Magnificent Mile**). Residences should be named after the person(s) occupying the residence. |
| *FacilityId* | Number (Integer) | A unique identifier for the particular building or campus of the lodging. Allows tracking whether a stay occurred at the same facility as another stay, even if the lodging was re-branded in between the stays. This also allows the lodging to be correlated with an external geospatial database, if one is used. |
| *Code* | Text | The unique identifier a Portfolio uses for this particular property, if available. Otherwise, this should be left blank. |
| *SabreGDS* | Text | For hotels and short-term rentals, the Sabre GDS identifier for the hotel at the time of the stay, if available. Otherwise, this should be left blank. |
| *Purpose* | Text | **Business** or **Personal**. |
| *Room* | Text | The room number(s) for this particular stay, if applicable. |
| *Qualifying* | Text | **Yes** or **No** (blanks are considered to be **Yes**). Whether the stay counts for status at the Portfolio. |
| *LifetimeQualifying* | Text | **Yes** or **No** (blanks are considered to be **Yes**). Whether the stay counts for lifetime status at the Portfolio. |
| *Comment* | Text | An optional comment field. |

If additional columns are desired, they should be named in PascalCase format.

#### Overnight Flights

A traveler may wake up the morning of a particular day on an overnight flight. These should be considered stays and kept as records on the *Stays* sheet.

In most cases, the CityId of a red-eye flight should be the airport where the flight arrives. Such a CityId should be recorded as **FLIGHT**, a forward slash, and the arrival IATA code (**FLIGHT/KEF**).

In certain situations, an overnight flight may last longer than a calendar day, such as some westbound flights across the International Date Line that land two calendar days after they depart. For example, consider a flight that departs DFW on 10 Feb (Dallas time) and lands in SYD on 12 Feb (Sydney time). The traveler’s CityId on the morning of 11 Feb should be recorded as the midpoint of the flight, represented as **FLIGHT**, a forward slash, and the IATA code of both airports separated by a hyphen (**FLIGHT/DFW-SYD**). The CityId for the morning of 12 February should be recorded as the arrival airport only (**FLIGHT/SYD**).

### Cities

Reference data for cities should be kept in a sheet titled _Cities_. The data should contain a row for each city, in a titled table with at least the following columns:

| Field | Format | Description |
|-------|--------|-------------|
| *Id* | Text | A unique identifier for each city as described in [City Format](#city-format). |
| *Name* | Text | The city’s name. |
| *Region* | Text | The city’s first-level administrative division (state, province, etc.) if appropriate for its country.
| *Country* | Text | The city’s country. |
| *Latitude* | Number | Latitude of the city in decimal degrees. |
| *Longitude* | Number | Longitude of the city in decimal degrees. |
| *CurrentMetro* | Text | The Id (as defined in the *Metros* sheet) of the city’s present-day metro area, or blank if the city is not presently in a metro area. |

### Metros

Reference data for metro areas should be kept in a sheet titled _Metros_. The data should contain a row for each metro area, in a titled table with at least the following columns:

| Field | Format | Description |
|-------|--------|-------------|
| *Id* | Text | A unique identifier for the metro area. Should always start with the ISO A2 country code and a slash, and typically then follows the city ID format for the metro area’s main city (**IS/REYKJAVIK**). However, if the country has its own ID scheme for metro areas, use that instead of a city name (**US/35620**). |
| *Title* | Title | The official name of the metro area, or the city name of the primary city if an official name is not available. |
| *ShortName* | Text | The name of the primary city of the metro area. |
| *Latitude* | Number | Latitude of the metro in decimal degrees. |
| *Longitude* | Number | Longitude of the metro in decimal degrees. |

### USStates

Reference data for U.S. states should be kept in a sheet titled _USStates_. The data should contain a row for each state, in a titled table with at least the following columns:

| Field | Format | Description |
|-------|--------|-------------|
| *Abbrev* | Text | Two-letter postal code for the state. |
| *Name* | Text | Name of the state. |
| *Latitude* | Number | Latitude of the state in decimal degrees. |
| *Longitude* | Number | Longitude of the state in decimal degrees. |

## City Format

City names should be formed of the following, in order:

- [ISO 3166 Alpha-2](https://www.iso.org/obp/ui/#search) country code
- Subdivision part of [ISO 3166-2](https://en.wikipedia.org/wiki/ISO_3166-2) subdivision code (if applicable)
- City name (capital A-Z and spaces only). US cities should use [USPS city name](https://tools.usps.com/zip-code-lookup.htm) if available.

All of the above should be separated by forward slashes. For example:

- **AU/NSW/SYDNEY**
- **IS/REYKJAVIK**
- **US/MO/SAINT LOUIS**
- **US/NC/WINSTON SALEM**

## Metro Format

If a country has a defined unique identifier for metro areas, then the metro ID should be the [ISO 3166 Alpha-2](https://www.iso.org/obp/ui/#search) country code, followed by a forward slash, followed by an identifier.

Otherwise, the metro ID should match the format of the city ID of the metro's principle city.

For example:

- **US/10740**
- **CA/TORONTO**
- **JP/KANTO**
