import pandas as pd
from datetime import date
from pathlib import Path
from date_distance_collection import DateDistanceCollection

HOTEL_FILE_PATH = Path("C:/Users/paulb/OneDrive/Documents/Travel/") / "Hotels.xlsx"
HOME_LOCATION = "Beavercreek, OH"

distances = DateDistanceCollection(2020, 2020, HOME_LOCATION)

distances.set_distance(date(2020,12,25), 5, "Chicago, IL")


for k, v in distances.distances.items():
    print(k, v)

# hotel_data_sheet = pd.read_excel(HOTEL_FILE_PATH, sheet_name='Hotel Data')
# hotel_data = hotel_data_sheet[['City', 'Checkout Date', 'Nights']]

# for row in hotel_data.values.tolist():
#     print(row)