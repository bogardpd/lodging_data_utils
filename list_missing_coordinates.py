"""Checks whether all hotel locations have coordinates defined."""
from modules.hotel_data_frame import HotelDataFrame
from modules.coordinates import all_coordinates
import numpy as np

def main():
    hotel_df = HotelDataFrame().df()
    hotel_cities = set(hotel_df['City'])

    coordinates = all_coordinates()
    coordinates_cities = set(coord_locations(coordinates))

    cities_without_coordinates = sorted(hotel_cities - coordinates_cities)
    if len(cities_without_coordinates) == 0:
        print("🆗 All hotel cities have coordinates defined.")
    else:
        print("Cities missing coordinates:")
        for city in cities_without_coordinates:
            print("\t", city)


def coord_locations(coordinates, parents=[], output=[]):
    for loc, sublocs in coordinates.items():
        loc_with_ancestors = [*parents, loc]
        if type(sublocs) is dict:
            coord_locations(sublocs, loc_with_ancestors, output)
        else:
            output.append("/".join(loc_with_ancestors))
    return output        
        

if __name__ == "__main__":
    main()