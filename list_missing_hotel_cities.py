"""Checks whether all hotel cities have entries in city data file."""
import colorama
import argparse
from modules.hotel_data_frame import HotelDataFrame
from modules.coordinates import all_coordinates

colorama.init(autoreset=True)

class MissingHotelCitiesError(Exception):
    pass

def main(args):
    hotel_df = HotelDataFrame().df()
    hotel_cities = set(hotel_df['city'])

    coordinates = all_coordinates()
    coordinates_cities = set(coordinates.index.values.tolist())

    cities_without_coordinates = sorted(hotel_cities - coordinates_cities)
    if len(cities_without_coordinates) == 0:
        print(colorama.Fore.GREEN + "All hotel cities have coordinates defined.")
    else:
        print("Cities missing coordinates:")
        if args.raiseException:
            raise MissingHotelCitiesError(
                f"Missing cities: {', '.join(cities_without_coordinates)}"
            )
        else:  
            for city in cities_without_coordinates:
                print(colorama.Fore.RED + f"  {city}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Check if every hotel location in spreadsheet has coords."
    )
    parser.add_argument('--raiseException',
        help="raise an exception if coordinates are missing",
        action='store_true',
    )
    args = parser.parse_args()
    main(args)