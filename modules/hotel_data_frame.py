import pandas as pd
from pathlib import Path
from datetime import timedelta

from modules.common import first_morning
from modules.coordinates import coordinates

class HotelDataFrame:
    """Manages a pandas dataframe of hotel stay data."""
    
    HOTEL_FILE_PATH = (Path.home()
        / Path("OneDrive/Documents/Travel/Hotels.xlsx"))

    def __init__(self, additional_columns=[]):
        """Initialize a HotelDataFrame."""
        
        # Read Excel spreadsheet.
        hotel_sheet = pd.read_excel(
            self.HOTEL_FILE_PATH,
            sheet_name='Hotel Data',
            parse_dates=['Checkout Date'],
        )
        
        # Normalize column names.
        hotel_sheet.columns = hotel_sheet.columns.str.replace(
            r'\s+', '_', regex=True
        ).str.lower()

        # Force checkout_date to be a date column.
        hotel_sheet.checkout_date = hotel_sheet.checkout_date.dt.date
        
        # Store sorted dataframe.
        columns = (['checkout_date', 'nights', 'city'] + additional_columns)
        self.data = hotel_sheet[columns].sort_values('checkout_date')

    def df(self):
        """Returns a Pandas DataFrame for hotel data."""
        return self.data

    def min_date(self):
        """Returns the earliest away date.

        This is one day after the checkin date for the first trip.
        """

        earliest_hotel_id = self.data['checkout_date'].idxmin()
        earliest_checkout = self.data.loc[
            earliest_hotel_id,'checkout_date'].date()
        earliest_nights = int(self.data.loc[earliest_hotel_id,'Nights'])
        
        return(first_morning(earliest_checkout, earliest_nights))

    def by_morning(self):
        """Returns a dataframe with a row for each morning away from
        home."""
        input_df = self.data
        stays = [
            pd.DataFrame.from_dict({
                'morning': [
                    row.checkout_date - timedelta(days=i)
                    for i in reversed(range(row.nights))
                ],
                'city': [row.city] * row.nights,
            })
            for row in input_df.itertuples()
        ]
        output = pd.concat(stays, ignore_index=True)
        output = output.set_index('morning')
        return output

    def location_frequencies(self,
                             reject_flight_midpoints=True,
                             start_date=None,
                             end_date=None):
        """Returns a dictionary with keys of cities and values of
        dictionaries with latitudes, longitudes, and locations."""
        
        frequencies = {}
        for row in self.data.values.tolist():
            nights = row[1]
            city = row[2]
            checkout = row[0].date()
            fm = first_morning(checkout, nights)
            if reject_flight_midpoints:
                location_list = city.split("/")
                if (location_list[0] == "Overnight Flight"
                        and "-" in location_list[1]):
                    continue
            if start_date:
                if checkout < start_date:
                    continue
                elif fm < start_date:
                    # Subtract number of nights before start date.
                    nights = nights - (start_date - fm).days
            if end_date:
                if fm > end_date:
                    continue
                elif checkout > end_date:
                    # Subtract number of nights after end date.
                    nights = nights - (checkout - end_date).days
                
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
