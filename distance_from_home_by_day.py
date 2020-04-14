from modules.collections import DateCollection
from modules.hotel_data_frame import HotelDataFrame
from datetime import date

OUTPUT_FILE_PATH = "output/distance_from_home_by_day.txt"
HOME_LOCATION = "US/OH/Beavercreek"

hotel_df = HotelDataFrame()
locations = DateCollection(hotel_df, date(2009,1,1), date(2020,12,31), HOME_LOCATION)

with open(OUTPUT_FILE_PATH, 'w') as f:
    for k, v in locations.distances().items():
        f.write (f"{k}\t{v}\n")
    print(f"Wrote to {OUTPUT_FILE_PATH}")