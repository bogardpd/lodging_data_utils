import pandas as pd

CITIES_PATH = "data/cities.csv"
METROS_PATH = "data/metro_areas.csv"
US_STATES_PATH = "data/us_states.csv"
LOCATION_COORDINATES = pd.read_csv(CITIES_PATH, index_col='city')

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
        print(f"\nPlease add it to {CITIES_PATH}.\n")
        raise SystemExit()