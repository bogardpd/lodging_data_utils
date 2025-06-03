# Lodging Data Structure

These scripts use two sources of data:

- A [Excel spreadsheet](#lodging-spreadsheet) containing stay, city, and metro data
- A [GeoPackage file](#lodging-geopackage) containing lodging location data

The location of these files is defined in [data_sources.toml](/data_sources.toml), with the keys `lodging_xlsx` and `lodging_gpkg` respectively.

## Lodging Spreadsheet

Stay, city, and metro data is stored in an Excel spreadsheet. The Excel file has the following sheets:

### Stays

Information for each stay should be stored in a sheet titled *Stays*. The data should contain a row for each lodging stay, in a titled table with at least the following columns:

| Column | Format | Description |
|--------|--------|-------------|
| *CheckoutDate* | Date | The departure date from the stay (in the lodging location’s time zone), in **YYYY-MM-DD** format. If departure occurs prior to midnight but the stay is booked/billed through the following morning, then the following morning should be used as the checkout date. |
| *Nights* | Number (Integer) | The number of nights spent on the stay. Should be equal to the difference in days between the check-in date and the check-out date. |
| *Type* | Text | **Hotel** (a hotel room), **STR** (Short Term Rental, such as Airbnb or VRBO), **Residence** (someone’s home), or **Flight** (as described in [Overnight Flights](#overnight-flights)).
| *Portfolio* | Text | The collection of hotel brands or short-term rentals, usually with its own loyalty program (e.g. **Hilton** or **VRBO**), that this lodging belongs to. Leave blank if this stay does not have a hotel portfolio. |
| *Brand* | Text | The brand of hotel (e.g. **Hampton Inn**). Short-term rentals will generally leave this blank. Hotels which are not part of a chain, residences, and overnight flights should leave this blank. |
| *Location* | Text | The name of the lodging. If the lodging is a chain hotel and the chain is part of the name, include the chain in the name (e.g. **Embassy Suites by Hilton Chicago Downtown Magnificent Mile**). Residences should be named after the person(s) occupying the residence. |
| *LodgingId* | Number (Integer) | An optional identifier, used to group stays that occurred at the same lodging instance. (This usually means a specific property, but different lodging instances could occupy the same property at different times as described in [Lodging Database Criteria for New vs. Updated Records](lodging_new_vs_updated_records.md).) May be used with an external geodata store (as described in [Lodging GeoPackage](#lodging-geopackage)) to match stays to feature IDs. |
| *CityId* | Text | The city where the lodging is located, as described in [City Format](#city-format). |
| *MetroId* | Text | The metro where the lodging is located as of the CheckoutDate, as described in [Metro Format](#city-format). |
| *Purpose* | Text | **Business** or **Personal**. |
| *Room* | Text | The room number(s) for this particular stay, if applicable. |
| *Qualifying* | Text | **Yes** or **No** (blanks are considered to be **Yes**). Whether the stay counts for status at the Portfolio. |
| *LifetimeQualifying* | Text | **Yes** or **No** (blanks are considered to be **Yes**). Whether the stay counts for lifetime status at the Portfolio. |
| *Comment* | Text | An optional comment field. |

If additional columns are desired, they should be named in PascalCase format.

> [!NOTE]
> The data for each stay should be accurate for the time the stay occurred. For example, if a hotel has since changed portfolios, the stay record should still reflect that hotel’s portfolio _at the time of the stay_.


#### Overnight Flights

A traveler may wake up the morning of a particular day on an overnight flight. These should be considered stays and kept as records in the `stays` table.

The flight stay should be associated with a `stay_location` located at the arrival airport. The `name` of such a location should be the airport where the flight arrives, formatted as `FLIGHT`, a forward slash, and the arrival IATA code (`FLIGHT/KEF`). This airport should have a `city` located on the airport, with a name formatted as `AIRPORT`, a forward slash, and the IATA code (`AIRPORT/KEF`). This airport city may belong to a `metro` and/or `region` if appropriate.

In certain situations, an overnight flight may last longer than a calendar day, such as some westbound flights across the International Date Line that land two calendar days after they depart. For example, consider a flight that departs DFW on 10 Feb (Dallas time) and lands in SYD on 12 Feb (Sydney time). The traveler’s `stay_location` on the morning of 11 Feb should be recorded as the midpoint of the flight, represented as `FLIGHT`, a forward slash, and the IATA code of both airports separated by a hyphen (`FLIGHT/DFW-SYD`). The `stay_location` for the morning of 12 February should be recorded as the arrival airport only and named `FLIGHT/SYD`. The midpoint location should _not_ be associated with a city, but the final location should be associated with a city.

### Cities

Reference data for cities should be kept in a sheet titled _Cities_. The data should contain a row for each city, in a titled table with at least the following columns:

| Field | Format | Description |
|-------|--------|-------------|
| *Id* | Text | A unique identifier for the city, as described in [City Format](#city-format). |
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
| *Id* | Text | A unique identifier for the metro area, as described in [Metro Format](#metro-format). |
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

## Lodging GeoPackage

Lodging location data is stored in a GeoPackage file.

### lodging_locations (Point)

The `lodging_locations` table stores information about distinct lodging properties, including hotels, residences, and short-term rentals.

| Column | Format | Description |
|--------|--------|-------------|
| *fid* | Number (Integer) | Primary key for the lodging location. Uniquely identifies each lodging property. |
| *geom* | Point | A point geometry representing the lodging location’s geographic coordinates (latitude/longitude). |
| *name* | Text | Full name of the lodging, including brand if part of the official property name (e.g. **Hilton Chicago O’Hare Airport**). |
| *type* | Text | The type of lodging: **Hotel**, **STR** (short-term rental), or **Residence**. |
| *city_id* | Text | The ID of the city where the lodging is located, using the format described in [City Format](#city-format). |
| *address* | Text | Full address of the lodging, including street, city, state, postal code, and country. |
| *brand* | Text | The brand of hotel, if applicable (e.g. **Holiday Inn**). May be blank for STRs and residences. |
| *portfolio* | Text | The loyalty program or hotel portfolio this lodging belongs to (e.g. **Marriott**, **IHG**, **Hilton**). May be blank. |
| *comments* | Text | Optional comment or note about the lodging location. |
| *portfolio_code* | Text | Internal or portfolio-specific identifier for the lodging location (e.g. a code used in loyalty systems). May be blank. |

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
