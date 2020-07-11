import json, operator
from functools import reduce

with open("data/coordinates.json", 'r', encoding="utf-8") as f:
    LOCATION_COORDINATES = json.load(f)

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