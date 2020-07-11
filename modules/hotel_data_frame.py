import pandas as pd
from pathlib import Path
from modules.common import first_morning
from modules.coordinates import coordinates

class HotelDataFrame:
    """Manages a pandas dataframe of hotel stay data."""
    
    HOTEL_FILE_PATH = (Path.home()
        / Path("OneDrive/Documents/Travel/Hotels.xlsx"))

    def __init__(self, additional_columns=[]):
        """Initialize a HotelDataFrame."""
        columns = (['Checkout Date', 'Nights', 'City']
            + additional_columns)
        hotel_data_sheet = pd.read_excel(
            self.HOTEL_FILE_PATH, sheet_name='Hotel Data')
        self.data = hotel_data_sheet[columns].sort_values(
            'Checkout Date')

    def min_date(self):
        """Returns the earliest away date.

        This is one day after the checkin date for the first trip.
        """

        earliest_hotel_id = self.data['Checkout Date'].idxmin()
        earliest_checkout = self.data.loc[
            earliest_hotel_id,'Checkout Date'].date()
        earliest_nights = int(self.data.loc[earliest_hotel_id,'Nights'])
        
        return(first_morning(earliest_checkout, earliest_nights))

    def location_frequencies(self, reject_flight_midpoints=True):
        """Returns a dictionary with keys of cities and values of
        dictionaries with latitudes, longitudes, and locations."""
        
        frequencies = {}
        for row in self.data.values.tolist():
            nights = row[1]
            city = row[2]
            if reject_flight_midpoints:
                location_list = city.split("/")
                if (location_list[0] == "Overnight Flight"
                        and "-" in location_list[1]):
                    continue
            if city in frequencies:
                frequencies[city]['frequency'] += nights
            else:
                latitude, longitude = coordinates(city)
                frequencies[city] = {
                    'latitude': latitude,
                    'longitude': longitude,
                    'frequency': nights,
                }

        return frequencies
