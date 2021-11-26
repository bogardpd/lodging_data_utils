import json, operator
from functools import reduce

COORDINATES_PATH = "data/coordinates.json"
with open(COORDINATES_PATH, 'r', encoding="utf-8") as f:
    LOCATION_COORDINATES = json.load(f)

def all_coordinates():
    """Returns a hash of all coordinates data."""
    return LOCATION_COORDINATES

def coordinates(city):
    """Returns the coordinates for a city as [lat, lon].
    
    City should be provided in 'US/CA/Los Angeles' format.
    """
    location_list = city.split("/")
    try:
        return(reduce(operator.getitem, location_list,
            LOCATION_COORDINATES))
    except KeyError as err:
        print(f"\nCould not find coordinates for:")
        print(city)
        print(f"\nPlease add it to {COORDINATES_PATH}.\n")
        raise SystemExit()