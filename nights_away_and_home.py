from modules.date_collection import DateCollection
from modules.hotel_data_frame import HotelDataFrame
from datetime import date

hotel_df = HotelDataFrame()
locations = DateCollection(hotel_df, date(2009,2,9), date.today())

for date, value in locations.locations.items():
    print(date, value)