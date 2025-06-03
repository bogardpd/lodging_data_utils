"""Defines the LodgingLog class for managing lodging information."""
import tomllib
import geopandas as gpd
import pandas as pd
import sqlite3
from pathlib import Path
from datetime import timedelta

ROOT = Path(__file__).parent.parent
with open(ROOT / "data_sources.toml", 'rb') as f:
    SOURCES = tomllib.load(f)

class LodgingLog:
    """A class to manage lodging information for a trip."""
    
    def __init__(self):
        """
        Initializes the LodgingLog.
        """
        
        self.lodging_path = Path(SOURCES['lodging_gpkg']).expanduser()
        self.mornings = self.__mornings()
        common_params = {
            'engine': 'pyogrio',
            'fid_as_index': True,
        }

        # Load the stay_locations data from the GeoPackage.
        self.stay_locations_gdf = gpd.read_file(
            self.lodging_path,
            layer='stay_locations',
            **common_params,
        )

    def __mornings(self):
        """
        Returns a DataFrame with a row for each morning away from home.
        """
        # Read an SQLite table into a DataFrame.
        conn = sqlite3.connect(self.lodging_path)
        query = """
        SELECT stays.fid as stay_fid, checkout_date, purpose, nights,
        stay_location_fid, city_fid, metro_fid, region_fid
        FROM stays
        JOIN stay_locations on stays.stay_location_fid = stay_locations.fid
        LEFT JOIN cities on stay_locations.city_fid = cities.fid
        ORDER BY checkout_date
        """
        dtypes = {
            'stay_fid': 'int64',
            'nights': 'int64',
            'stay_location_fid': 'int64',
            'city_fid': 'Int64',
            'metro_fid': 'Int64',
            'region_fid': 'Int64',
        }
        stays = pd.read_sql_query(query, conn,
            parse_dates=['checkout_date'], dtype=dtypes,
        )
        stay_frames = [
            pd.DataFrame.from_dict({
                'morning': [
                    row.checkout_date - timedelta(days=i)
                    for i in reversed(range(row.nights))
                ],
                'stay_fid': [row.stay_fid] * row.nights,
                'purpose': [row.purpose] * row.nights,
                'stay_location_fid': [row.stay_location_fid] * row.nights,
                'city_fid': [row.city_fid] * row.nights,
                'metro_fid': [row.metro_fid] * row.nights,
                'region_fid': [row.region_fid] * row.nights,
            })
            for row in stays.itertuples()
        ]
        output = pd.concat(stay_frames, ignore_index=True)
        output = output.set_index('morning')
        return output


       