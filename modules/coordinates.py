import pandas as pd
import tomllib
import sqlite3
from pathlib import Path

ROOT = Path(__file__).parent.parent
with open(ROOT / "data_sources.toml", 'rb') as f:
    sources = tomllib.load(f)

lodging_path = Path(sources['lodging_xlsx']).expanduser()
LOCATION_COORDINATES = pd.read_excel(
    lodging_path,
    sheet_name='Cities',
).set_index('Id')

def all_coordinates():
    """Returns a hash of all coordinates data."""
    return LOCATION_COORDINATES

def coordinates(city):
    """Returns the coordinates for a city as [lat, lon].
    
    City should be provided in 'US/CA/LOS ANGELES' format.
    """
    try:
        row = LOCATION_COORDINATES.loc[city]
        return([row.Latitude,row.Longitude])
    except KeyError as err:
        print(f"\nCould not find coordinates for:")
        print(city)
        print(f"\nPlease add it to {lodging_path}.\n")
        raise SystemExit()