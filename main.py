import pandas as pd
from pathlib import Path
from date_distance_collection import DateDistanceCollection

HOTEL_FILE_PATH = Path("C:/Users/paulb/OneDrive/Documents/Travel/") / "Hotels.xlsx"

distances = DateDistanceCollection(2009, 2020)

for k, v in distances.distances.items():
    print(k, v)

hotel_data_sheet = pd.read_excel(HOTEL_FILE_PATH, sheet_name='Hotel Data')
hotel_data = hotel_data_sheet[['City', 'Checkout Date', 'Nights']]

# for row in hotel_data.values.tolist():
#     print(row)