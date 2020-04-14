"""Contains classes for creating various collections of hotel data."""

import json, math, operator
from modules.common import checkin_date
from modules.common import first_morning
from datetime import date
from dateutil import rrule
from functools import reduce


class DateCollection:
    """Manages a range of dates with a location assigned to each."""
    
    COORDINATES_PATH = "data/coordinates.json"
    DEG_TO_RAD = math.pi / 180
    EARTH_MEAN_RADIUS = 3958.7613 # miles
        
    def __init__(self, hotel_df, start_date, end_date, default_location=None):
        """Initialize a DateCollection."""
        
        with open(self.COORDINATES_PATH, 'r', encoding="utf-8") as f:
            self.location_coordinates = json.load(f)
        
        self._hotel_df = hotel_df
        self._default_value = None if default_location == None else {
            'city': default_location,
            'coordinates': self._coordinates(default_location)}
        # Create dictionary of dates with locations set to None by default:
        self.locations = {d:self._default_value for d in self._inclusive_date_range(
            start_date, end_date)}

        # Set locations from hotel data:
        for row in self._hotel_df.data.values.tolist():
            self._set_location(*row)

    def _coordinates(self, location):
        """Returns the coordinates for a location."""
        location_list = location.split("/")
        try:
            return(reduce(operator.getitem, location_list,
                self.location_coordinates))
        except KeyError as err:
            print(f"\nCould not find coordinates for:")
            print(location)
            print(f"\nPlease add it to {self.COORDINATES_PATH}.\n")
            raise SystemExit()
    
    def _home_distance(self, location):
        """Returns the distance from home to the provided location.
        
        The Haversine formula is used to calculate the distance.
        """
        home_coordinates = self._default_value['coordinates']
        location_coordinates = self._coordinates(location)
        phi_1 = home_coordinates[0] * self.DEG_TO_RAD
        phi_2 = location_coordinates[0] * self.DEG_TO_RAD
        delta_phi = (
            (location_coordinates[0] - home_coordinates[0])
            * self.DEG_TO_RAD)
        delta_lambda = (
            (location_coordinates[1] - home_coordinates[1])
            * self.DEG_TO_RAD)
        a = (math.sin(delta_phi/2)**2
            + math.cos(phi_1)
            * math.cos(phi_2)
            * math.sin(delta_lambda/2)**2)
        distance = (2
            * self.EARTH_MEAN_RADIUS
            * math.atan2(math.sqrt(a), math.sqrt(1-a)))
        return distance

    def _inclusive_date_range(self, start_date, end_date):
        """Returns a list of date objects in the given range."""
        return([d.date() for d in list(rrule.rrule(rrule.DAILY,
            dtstart=start_date, until=end_date))])

    def _set_location(self, checkout_date, nights, location):
        """ Sets the locations for the dates in a given hotel stay."""
        dates = self._inclusive_date_range(
            first_morning(checkout_date, nights),
            checkout_date)
        
        for day in dates:
            if day in self.locations.keys():
                self.locations[day] = {
                    'city': location,
                    'coordinates': self._coordinates(location)}

    def distances(self):
        """Returns a dictionary of dates and distance from home.

        The distance from home is in miles.
        """
        if self._default_value == None:
            raise TypeError(
                "default_location must be set in order to calculate distances")
        distances = {}
        for date, loc in self.locations.items():
            distances[date] = self._home_distance(loc['city'])
        return distances


class GroupedStayCollection:
    """Groups consecutive away-from-home stays.
        
        Creates an array of dictionaries of away period/home period
        pairs, with details for each in nested dictionaries.
        """
    END_DATE = date.today()

    def __init__(self, hotel_data_frame):
        """Initialize a GroupedStayCollection."""
        self.groups = self._group_stays(hotel_data_frame)
        
    def _group_stays(self, hotel_data_frame):
        """Groups consecutive away-from-home stays."""
        grouped = []
        previous_checkout = None
        for stay in hotel_data_frame.data.values.tolist():
            checkout = stay[0].date()
            nights = stay[1]
            city = stay[2]
            purpose = stay[3]
            checkin = checkin_date(checkout, nights)

            if (len(grouped) == 0) or checkin != previous_checkout:
                # Create new group:
                
                grouped.append({
                    'start': checkin,
                    'end': checkout,
                    'nights': (checkout - checkin).days,
                    'cities': [{
                        'city': city,
                        'purpose': purpose,
                        'start': checkin,
                        'end': checkout,
                        'nights': (checkout - checkin).days
                        }]
                    })
                    
            else:
                # Merge into previous group:
                grouped[-1]['end'] = checkout
                grouped[-1]['nights'] = (checkout - grouped[-1]['start']).days
                
                if (len(grouped[-1]['cities']) == 0
                        or grouped[-1]['cities'][-1]['city'] != city
                        or grouped[-1]['cities'][-1]['purpose'] != purpose):

                    # Create a new city:
                    grouped[-1]['cities'].append({
                        'city': city,
                        'purpose': purpose,
                        'start': checkin,
                        'end': checkout,
                        'nights': (checkout - checkin).days
                    })
                else:
                    # Merge into previous city:
                    grouped[-1]['cities'][-1]['end'] = checkout
                    grouped[-1]['cities'][-1]['nights'] = (
                        checkout - grouped[-1]['cities'][-1]['start']).days

            previous_checkout = checkout
        return grouped
    
    def rows(self):
        """Creates a row for each away period/home period pair.

        Calculates the length of each home stay between two away groups.
        """
        away_home_rows = []
        for i, group in enumerate(self.groups):
            home_start = group['end']
            if i == len(self.groups) - 1:
                home_end = self.END_DATE 
            else:
                home_end = self.groups[i + 1]['start']
            away_nights = (group['end'] - group['start']).days
            away = group
            home = {
                'start': home_start,
                'end': home_end,
                'nights': (home_end - home_start).days
            }
            away_home_rows.append({'away': away, 'home': home})
        return(away_home_rows)