import pandas as pd
from datetime import date
from pathlib import Path
from modules.date_collection import DateCollection

HOTEL_FILE_PATH = Path("C:/Users/paulb/OneDrive/Documents/Travel/") / "Hotels.xlsx"
OUTPUT_FILE_PATH = "output/heatmap_data.csv"

hotel_data_sheet = pd.read_excel(HOTEL_FILE_PATH, sheet_name='Hotel Data')
hotel_data = hotel_data_sheet[['Checkout Date', 'Nights', 'City']]

earliest_hotel_id = hotel_data['Checkout Date'].idxmin()
earliest_checkout = hotel_data.loc[earliest_hotel_id,'Checkout Date'].date()
earliest_nights = int(hotel_data.loc[earliest_hotel_id,'Nights'])

min_date = DateCollection.first_morning(
    earliest_checkout, earliest_nights)

locations = DateCollection(min_date, date.today())
# locations = DateCollection(min_date, date.today(), "US/OH/Beavercreek")

for row in hotel_data.values.tolist():
    locations.set_location(*row)

with open(OUTPUT_FILE_PATH, 'w') as f:
    f.write("Date,Latitude,Longitude\n")
    for date, location in locations.locations.items():
        if location != None:
            f.write(f"{date},{location['coordinates'][0]},{location['coordinates'][1]}\n")
    print(f"Wrote to {OUTPUT_FILE_PATH}")