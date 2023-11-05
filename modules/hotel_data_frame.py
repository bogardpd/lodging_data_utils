import pandas as pd
import tomllib
from pathlib import Path
from datetime import timedelta

from modules.common import first_morning
from modules.coordinates import coordinates

with open(Path(__file__).parent.parent / "config.toml", 'rb') as f:
    config = tomllib.load(f)

class HotelDataFrame:
    """Manages a pandas dataframe of hotel stay data."""
    
    HOTEL_FILE_PATH = Path(config['files']['lodging_data']).expanduser()

    def __init__(self, additional_columns=[]):
        """Initialize a HotelDataFrame."""
        
        # Read Excel spreadsheet.
        hotel_sheet = pd.read_excel(
            self.HOTEL_FILE_PATH,
            sheet_name='Stays',
            parse_dates=['CheckoutDate'],
        )

        # Force checkout_date to be a date column.
        hotel_sheet.CheckoutDate = hotel_sheet.CheckoutDate.dt.date

        # Force city ID to be uppercase.
        hotel_sheet['City'] = hotel_sheet['City'].str.upper()
        
        # Store sorted dataframe.
        columns = (['CheckoutDate', 'Nights', 'City'] + additional_columns)
        self.data = hotel_sheet[columns].sort_values('CheckoutDate')

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
                    row.CheckoutDate - timedelta(days=i)
                    for i in reversed(range(row.Nights))
                ],
                'city': [row.City] * row.Nights,
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
                if (location_list[0] == "FLIGHT"
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
