"""Defines the LodgingLog class for managing lodging information."""

# Standard library imports
import sqlite3
from pathlib import Path
from datetime import datetime, timedelta
from typing import cast

# Third-party imports
import tomllib
import geopandas as gpd
import pandas as pd

ROOT = Path(__file__).parent.parent
with open(ROOT / "config" / "data_sources.toml", 'rb') as f:
    SOURCES = tomllib.load(f)

TRANSIT_TYPES = ['Flight']

class LodgingLog:
    """A class to manage lodging information for a trip."""

    def __init__(self):
        """Initializes the LodgingLog."""
        self.lodging_path = Path(SOURCES['lodging_gpkg']).expanduser()
        self._validate()
        self.dtypes = {
            'stay_fid': 'int64',
            'nights': 'int64',
            'stay_location_fid': 'int64',
            'city_fid': 'Int64',
            'metro_fid': 'Int64',
            'region_fid': 'Int64',
        }

        # Store geodata in a cache for quick access.
        # This avoids reading the GeoPackage multiple times.
        self.geodata_cache = {
            'stay_locations': self.geodata('stay_locations'),
            'cities': self.geodata('cities'),
            'metros': self.geodata('metros'),
            'regions': self.geodata('regions'),
        }

    def __repr__(self):
        """Returns a string representation of the LodgingLog."""
        return f"LodgingLog(lodging_path={self.lodging_path})"

    def __str__(self):
        """Returns a string representation of the LodgingLog."""
        return f"LodgingLog at {self.lodging_path}"

    def geodata(self, layer):
        """Returns a GeoDataFrame for the specified layer in the
        GeoPackage.

        Args:
            layer (str): The name of the layer to read from the
            GeoPackage.

        Returns:
            GeoDataFrame: A GeoDataFrame containing the data from the
            specified layer.
        """
        gdf = gpd.read_file(
            self.lodging_path,
            layer=layer,
            engine='pyogrio',
            fid_as_index=True
        )
        # Convert id columns to Int64.
        for col in ['city_fid', 'metro_fid', 'region_fid']:
            if col in gdf.columns:
                gdf[col] = gdf[col].astype('Int64')

        return gdf

    def mornings(self) -> pd.DataFrame:
        """Returns a DataFrame with a row for each morning away from
        home.
        """
        # Read an SQLite table into a DataFrame.
        conn = sqlite3.connect(self.lodging_path)
        query = """
        SELECT stays.fid as stay_fid, check_out_date, purpose, nights,
        stay_location_fid, type, city_fid, metro_fid, region_fid, absence_flags
        FROM stays
        JOIN stay_locations on stays.stay_location_fid = stay_locations.fid
        LEFT JOIN cities on stay_locations.city_fid = cities.fid
        ORDER BY check_out_date
        """

        stays = pd.read_sql_query(query, conn,
            parse_dates=['check_out_date'],
            dtype={
                'stay_fid': pd.Int64Dtype(),
                'nights': pd.Int64Dtype(),
                'stay_location_fid': pd.Int64Dtype(),
                'city_fid': pd.Int64Dtype(),
                'metro_fid': pd.Int64Dtype(),
                'region_fid': pd.Int64Dtype(),
                'check_out_date': 'datetime64[ns]',
                'absence_flags': pd.StringDtype(),
            },
        )
        conn.close()

        # Create a DataFrame for each stay, expanding the mornings.
        stay_frames = []
        for row in stays.itertuples():
            mornings = self._stay_mornings(row)
            present_nights = len(mornings)
            if present_nights == 0:
                continue
            stay_frames.append(
                pd.DataFrame.from_dict({
                    'morning': mornings,
                    'stay_fid': [row.stay_fid] * present_nights,
                    'purpose': [row.purpose] * present_nights,
                    'type': [row.type] * present_nights,
                    'stay_location_fid': (
                        [row.stay_location_fid] * present_nights
                    ),
                    'city_fid': [row.city_fid] * present_nights,
                    'metro_fid': [row.metro_fid] * present_nights,
                    'region_fid': [row.region_fid] * present_nights,
                })
            )

        # Concatenate all stay DataFrames into a single DataFrame.
        output = pd.concat(stay_frames, ignore_index=True)
        output = output.sort_values(by='morning')

        # Check for duplicate mornings.
        duplicates = output[output['morning'].duplicated(keep=False)]
        if not duplicates.empty:
            raise ValueError(
                "Duplicate mornings found in stays:\n"
                f"{duplicates[['morning', 'stay_fid']].to_string(index=False)}"
            )

        # Convert the 'morning' column to datetime and set it as the index.
        output = output.set_index('morning')
        output.index = pd.to_datetime(output.index)

        return output

    def mornings_by(self,
        by='location',
        start_morning=None,
        thru_morning=None,
        exclude_transit=False,
    ):
        """Returns a DataFrame with a row for each morning away from
        home, grouped by the specified location type.
        """
        if by not in ['location', 'city', 'metro', 'region']:
            raise ValueError(f"Invalid grouping type: {by}")
        mornings = self.mornings().loc[start_morning:thru_morning]
        if exclude_transit:
            mornings = mornings[
                ~mornings.type.isin(TRANSIT_TYPES)
            ]

        # Get the attributes of each location row.
        mornings[
            ['place_type', 'type_fid', 'title', 'name', 'key', 'lat', 'lon']
        ] = mornings.apply(
            lambda row: self.location_attrs(row, by),
            axis=1,
            result_type='expand',
        )

        return mornings

    def home_locations(self):
        """Returns a DataFrame with the location of all homes.
        Latitude and longitude are derived from the city if available,
        otherwise from the stay_location.
        """
        def get_home_location(row):
            """Returns the home location based on city or stay_location."""
            if pd.notna(row.city_fid):
                geom = self.geodata_cache['cities'].loc[row.city_fid].geometry
            else:
                geom = self.geodata_cache['stay_locations'].loc[
                    row.stay_location_fid
                ].geometry
            return (geom.y, geom.x)

        # Read an SQLite table into a DataFrame.
        conn = sqlite3.connect(self.lodging_path)
        query = """
        SELECT homes.fid as home_fid, move_in_date, stay_location_fid,
        city_fid, metro_fid, region_fid
        FROM homes
        JOIN stay_locations on homes.stay_location_fid = stay_locations.fid
        LEFT JOIN cities on stay_locations.city_fid = cities.fid
        ORDER BY move_in_date
        """
        home_locations = pd.read_sql_query(query, conn,
            parse_dates=['move_in_date'],
            dtype={
                'home_fid': pd.Int64Dtype(),
                'move_in_date': 'datetime64[ns]',
                'stay_location_fid': pd.Int64Dtype(),
                'city_fid': pd.Int64Dtype(),
                'metro_fid': pd.Int64Dtype(),
                'region_fid': pd.Int64Dtype(),
            },
        )
        home_locations[['lat', 'lon']] = home_locations.apply(
            get_home_location,
            axis=1,
            result_type='expand',
        )
        print(home_locations)
        return home_locations

    def location_attrs(self, row, by):
        """Get the attributes of each location row."""
        priority = {
            'location': ['stay_location'],
            'city': ['city', 'stay_location'],
            'metro': ['metro', 'city', 'stay_location'],
            'region': ['region', 'city', 'stay_location'],
        }
        place_types = {
            'stay_location': {
                'name': 'StayLocation',
                'fid': 'stay_location_fid',
                'table': 'stay_locations',
                'cols': {
                    'key': 'fid',
                    'name': 'name',
                    'title': None,
                },
            },
            'city': {
                'name': 'City',
                'fid': 'city_fid',
                'table': 'cities',
                'cols': {
                    'key': 'key',
                    'name': 'name',
                    'title': None,
                },
            },
            'metro': {
                'name': 'Metro',
                'fid': 'metro_fid',
                'table': 'metros',
                'key_col': 'key',
                'title_col': 'name','cols': {
                    'key': 'key',
                    'name': 'name',
                    'title': 'title',
                },
            },
            'region': {
                'name': 'Region',
                'fid': 'region_fid',
                'table': 'regions',
                'cols': {
                    'key': 'iso_3166',
                    'name': 'name',
                    'title': None,
                },
            },
        }
        for place_type in priority[by]:
            if pd.notnull(row[place_types[place_type]['fid']]):
                type_fid = row[place_types[place_type]['fid']]
                table = place_types[place_type]['table']
                record = self.geodata_cache[table].loc[type_fid]
                col_vals = {}
                for k, v in place_types[place_type]['cols'].items():
                    if v is None:
                        col_vals[k] = pd.NA
                    else:
                        if v == 'fid':
                            col_vals[k] = type_fid
                        else:
                            col_vals[k] = record[v]
                geometry = record.geometry
                if geometry is None:
                    lat = pd.NA
                    lon = pd.NA
                else:
                    lat = geometry.y
                    lon = geometry.x
                return (
                    place_types[place_type]['name'],
                    f"{place_type}_{type_fid}",
                    col_vals['title'],
                    col_vals['name'],
                    col_vals['key'],
                    lat,
                    lon,
                )
        return (pd.NA, pd.NA, pd.NA, pd.NA, pd.NA, pd.NA)

    def _stay_mornings(self, row) -> list[datetime]:
        """Returns a list of mornings for a given stay row.
        Takes into account any absence flags.

        Args:
            row: A row from the stays DataFrame.

        Returns:
            A list of datetime objects representing the mornings for the stay.
        """
        # Generate a list of mornings based on the check_out_date and nights.
        morning_list = [
            cast(datetime, row.check_out_date) - timedelta(days=i)
            for i in reversed(range(cast(int, row.nights)))
        ]
        # If absence_flags is not null, filter the mornings based on presence.
        # 'P' indicates presence, 'A' indicates absence.
        if pd.notnull(row.absence_flags):
            absence_flags = list(row.absence_flags)
            morning_list = [
                morning_list[i]
                for i in range(len(morning_list))
                if absence_flags[i] == 'P'
            ]

        return morning_list

    def _validate(self):
        """Validates the LodgingLog data."""
        with open(ROOT / "config" / "validations.toml", 'rb') as vf:
            validations = tomllib.load(vf)['validations']
        conn = sqlite3.connect(self.lodging_path)

        for validation in validations:
            query = validation['query']
            invalid_data = pd.read_sql_query(query, conn,
                dtype={'fid': 'int64'},
            )
            if not invalid_data.empty:
                table = validation['table']
                error = validation['error']
                raise ValueError(
                    f"Invalid data found in table '{table}' ({error}):\n"
                    f"{invalid_data.to_string(index=False)}"
                )

        conn.close()
        return True
