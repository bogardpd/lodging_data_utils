import pandas as pd
import tomllib
import sqlite3
from pathlib import Path

with open(Path(__file__).parent.parent / "config.toml", 'rb') as f:
    config = tomllib.load(f)

db_path = Path(config['files']['location_db']).expanduser()
con = sqlite3.connect(db_path)
sql_loc = "SELECT * FROM cities ORDER BY city_id"
LOCATION_COORDINATES = pd.read_sql(sql_loc, con).set_index('city_id')

def all_coordinates():
    """Returns a hash of all coordinates data."""
    return LOCATION_COORDINATES

def coordinates(city):
    """Returns the coordinates for a city as [lat, lon].
    
    City should be provided in 'US/CA/Los Angeles' format.
    """
    try:
        row = LOCATION_COORDINATES.loc[city]
        return([row.latitude,row.longitude])
    except KeyError as err:
        print(f"\nCould not find coordinates for:")
        print(city)
        print(f"\nPlease add it to {db_path}.\n")
        raise SystemExit()