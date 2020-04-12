import pandas as pd
from pathlib import Path
from modules.common import first_morning

class HotelDataFrame:
    """Manages a pandas dataframe of hotel stay data."""

    HOTEL_FILE_PATH = (Path("C:/Users/paulb/OneDrive/Documents/Travel/")
    / "Hotels.xlsx")

    def __init__(self):
        """Initialize a HotelDataFrame."""
        hotel_data_sheet = pd.read_excel(
            self.HOTEL_FILE_PATH, sheet_name='Hotel Data')
        self.data = hotel_data_sheet[
            ['Checkout Date', 'Nights', 'City']].sort_values('Checkout Date')

    def min_date(self):
        """Returns the earliest away date.

        This is one day after the checkin date for the first trip.
        """

        earliest_hotel_id = self.data['Checkout Date'].idxmin()
        earliest_checkout = self.data.loc[
            earliest_hotel_id,'Checkout Date'].date()
        earliest_nights = int(self.data.loc[earliest_hotel_id,'Nights'])
        
        return(first_morning(
            earliest_checkout, earliest_nights))
