from datetime import date
from modules.collections import DateCollection
from modules.hotel_data_frame import HotelDataFrame

OUTPUT_FILE_PATH = "output/heatmap_data.csv"

hotel_df = HotelDataFrame()
min_date = hotel_df.min_date()

locations = DateCollection(hotel_df, min_date, date.today())
# locations = DateCollection(min_date, date.today(), "US/OH/Beavercreek")

with open(OUTPUT_FILE_PATH, 'w') as f:
    f.write("Date,Latitude,Longitude,City\n")
    for date, location in locations.locations.items():
        if location != None:
            f.write(f"{date},"
            f"{location['coordinates'][0]},"
            f"{location['coordinates'][1]},"
            f"{location['city']}\n")
    print(f"Wrote to {OUTPUT_FILE_PATH}")