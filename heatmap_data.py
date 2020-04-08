from datetime import date
from modules.date_collection import DateCollection
from modules.hotel_data_frame import HotelDataFrame

OUTPUT_FILE_PATH = "output/heatmap_data.csv"

hotel_df = HotelDataFrame()
min_date = hotel_df.min_date()

locations = DateCollection(min_date, date.today())
# locations = DateCollection(min_date, date.today(), "US/OH/Beavercreek")

for row in hotel_df.data.values.tolist():
    locations.set_location(*row)

with open(OUTPUT_FILE_PATH, 'w') as f:
    f.write("Date,Latitude,Longitude\n")
    for date, location in locations.locations.items():
        if location != None:
            f.write(f"{date},"
            f"{location['coordinates'][0]},"
            f"{location['coordinates'][1]}\n")
    print(f"Wrote to {OUTPUT_FILE_PATH}")