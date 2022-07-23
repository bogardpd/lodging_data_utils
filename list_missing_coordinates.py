"""Checks whether all hotel locations have coordinates defined."""
from modules.hotel_data_frame import HotelDataFrame
from modules.coordinates import all_coordinates
import numpy as np

def main():
    hotel_df = HotelDataFrame().df()
    hotel_cities = set(hotel_df['city'])

    coordinates = all_coordinates()
    coordinates_cities = set(coordinates.index.values.tolist())

    cities_without_coordinates = sorted(hotel_cities - coordinates_cities)
    if len(cities_without_coordinates) == 0:
        print("🆗 All hotel cities have coordinates defined.")
    else:
        print("Cities missing coordinates:")
        for city in cities_without_coordinates:
            print("\t", city)        

if __name__ == "__main__":
    main()