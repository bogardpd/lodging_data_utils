from modules.date_collection import DateDistanceCollection
from modules.hotel_data_frame import HotelDataFrame

OUTPUT_FILE_PATH = "output/distance_from_home_by_day.txt"
HOME_LOCATION = "US/OH/Beavercreek"

hotel_df = HotelDataFrame()
locations = DateDistanceCollection(2009, 2020, HOME_LOCATION)

for row in hotel_df.data.values.tolist():
    locations.set_location(*row)

with open(OUTPUT_FILE_PATH, 'w') as f:
    for k, v in locations.locations.items():
        f.write (f"{k}\t{v}\n")
    print(f"Wrote to {OUTPUT_FILE_PATH}")