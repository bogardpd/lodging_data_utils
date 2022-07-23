"""Contains classes for creating various collections of hotel data."""

import math
from modules.common import checkin_date
from modules.common import first_morning
from modules.common import inclusive_date_range
from modules.common import stay_mornings
from modules.coordinates import coordinates
from datetime import date
from dateutil import rrule


class DateCollection:
    """Manages a range of dates with a location assigned to each."""
    
    DEG_TO_RAD = math.pi / 180
    EARTH_MEAN_RADIUS = 3958.7613 # miles
        
    def __init__(self, hotel_df, start_date, end_date, default_location=None):
        """Initialize a DateCollection."""
        
        self._hotel_df = hotel_df
        self._default_value = None if default_location == None else {
            'city': default_location,
            'coordinates': coordinates(default_location)}
        # Create dictionary of dates with locations set to None by default:
        self.locations = {d:self._default_value for d in inclusive_date_range(
            start_date, end_date)}

        # Set locations from hotel data:
        for row in self._hotel_df.data.values.tolist():
            self._set_location(*row)
    
    def _home_distance(self, location):
        """Returns the distance from home to the provided location.
        
        The Haversine formula is used to calculate the distance.
        """
        home_coordinates = self._default_value['coordinates']
        location_coordinates = coordinates(location)
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

    def _set_location(self, checkout_date, nights, location):
        """ Sets the locations for the dates in a given hotel stay."""
        dates = stay_mornings(
            checkin_date(checkout_date, nights), checkout_date)
        
        for day in dates:
            if day in self.locations.keys():
                self.locations[day] = {
                    'city': location,
                    'coordinates': coordinates(location)}

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
            print(stay)
            checkout = stay[0]
            nights = stay[1]
            city = stay[2]
            purpose = stay[3]
            checkin = checkin_date(checkout, nights)

            if (len(grouped) == 0) or checkin != previous_checkout:
                # Create new StayPeriod:
                grouped.append(
                    StayPeriod(True, checkout, nights, city, purpose))
            else:
                # Merge into previous group:
                grouped[-1].merge_stay(checkout, nights, city, purpose)

            previous_checkout = checkout
        
        return grouped
    
    def rows(self):
        """Creates a row for each away period/home period pair.

        Calculates the length of each home stay between two away groups.
        """
        away_home_rows = []
        for i, group in enumerate(self.groups):
            home_start = group.end            
            if i == len(self.groups) - 1:
                home_end = self.END_DATE 
            else:
                home_end = self.groups[i + 1].start
            home_nights = (home_end - home_start).days
            
            away = group            
            home = StayPeriod(False, home_end, home_nights)

            away_home_rows.append({'away': away, 'home': home})
        return(away_home_rows)
    

class StayPeriod:
    """Contains details for a single home or away stay period.
    
    An away stay period may have multiple back to back hotel stays.
    """

    def __init__(self, is_away, checkout_date, nights, city=None,
                    purpose=None):
        """Initializes a Stay."""
        self.is_away = is_away
        self.end = checkout_date
        self.nights = nights

        self.start = checkin_date(self.end, nights)

        if is_away:
            self.cities = [{
                'city': city,
                'purpose': purpose,
                'start': self.start,
                'end': self.end,
                'nights': self.nights
            }]            
        else:
            self.cities = []

    def __str__(self):
        """Returns a StayPeriod as a string."""
        period_type = "Away" if self.is_away else "Home"
        date_format = "%a %d %b %Y"
    
        return (f"{period_type} {self.start.strftime(date_format)} - "
            f"{self.end.strftime(date_format)} ({self.nights} nights)")

    def away_purposes(self):
        """Returns a list of the purpose of each night of a StayPeriod.

        Used to color code away night dots by trip purpose.
        """
        if self.is_away == False:
            return(None)
        away_purposes = []
        for loc in self.cities:
            away_purposes.extend(
                loc['purpose'].lower() for i in range(loc['nights']))
        return(away_purposes)

    def date_range_string(self):
        """Returns a formatted string for the stay start and end dates.
        """
        start = self.start
        end = self.end
        if start.year == end.year:
            if start.month == end.month:
                start_str = str(start.day)
            else:
                start_str = f"{start.day} {start:%b}"
        else:
            start_str = f"{start.day} {start:%b} {start.year}"
        end_str = f"{end.day} {end:%b} {end.year}"
        return(f"{start_str}–{end_str}")

    def first_morning(self):
        """Returns the first morning of the stay period.

        This is the date after the checkin date.
        """
        return(first_morning(self.end, self.nights))

    def merge_stay(self, stay_checkout_date, nights, city, purpose):
        """Merges another location into this away stay."""

        stay_checkin_date = checkin_date(stay_checkout_date, nights)
        if stay_checkin_date != self.end:
            raise ValueError("Can't merge two stays that are not adjacent!")

        self.end = stay_checkout_date
        self.nights = (stay_checkout_date - self.start).days

        if (len(self.cities) == 0
                or self.cities[-1]['city'] != city
                or self.cities[-1]['purpose'] != purpose):
            # Create a new city:
            self.cities.append({
                'city': city,
                'purpose': purpose,
                'start': stay_checkin_date,
                'end': stay_checkout_date,
                'nights': (stay_checkout_date - stay_checkin_date).days
            })
        else:
            # Merge into previous city:
            self.cities[-1]['end'] = stay_checkout_date
            self.cities[-1]['nights'] = (
                stay_checkout_date - self.cities[-1]['start']).days

    def mornings(self):
        """Return a list containing all morning dates during the stay.

        The checkin date is not included.
        """
        return(stay_mornings(self.start, self.end))