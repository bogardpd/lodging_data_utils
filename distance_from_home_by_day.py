import pandas as pd
from datetime import date
from pathlib import Path
from modules.date_distance_collection import DateDistanceCollection

HOTEL_FILE_PATH = Path("C:/Users/paulb/OneDrive/Documents/Travel/") / "Hotels.xlsx"
OUTPUT_FILE_PATH = "output/distance_from_home_by_day.txt"
HOME_LOCATION = "US/OH/Beavercreek"

distances = DateDistanceCollection(2009, 2020, HOME_LOCATION)

hotel_data_sheet = pd.read_excel(HOTEL_FILE_PATH, sheet_name='Hotel Data')
hotel_data = hotel_data_sheet[['Checkout Date', 'Nights', 'City']]

for row in hotel_data.values.tolist():
    distances.set_distance(*row)

with open(OUTPUT_FILE_PATH, 'w') as f:
    for k, v in distances.distances.items():
        f.write (f"{k}\t{v}\n")
    print(f"Wrote to {OUTPUT_FILE_PATH}")