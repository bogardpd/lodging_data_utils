import json, math, operator
from datetime import date, timedelta
from dateutil import rrule
from functools import reduce


def first_morning(checkout_date, nights):
    """Returns the date one day after checkin."""
    return(checkout_date - timedelta(days=(nights-1)))


class DateCollection:
    """Manages a range of dates with a location assigned to each."""
    
    COORDINATES_PATH = "data/coordinates.json"
    EARTH_MEAN_RADIUS = 3958.7613 # miles
    DEG_TO_RAD = math.pi / 180

    def __init__(self, start_date, end_date, default_location=None):
        """Initialize a DateCollection."""
        
        with open(self.COORDINATES_PATH, 'r', encoding="utf-8") as f:
            self.location_coordinates = json.load(f)
        
        default_value = None if default_location == None else {
            'city': default_location,
            'coordinates': self.__coordinates(default_location)}
        # Create dictionary of dates with locations set to None by default:
        self.locations = {d:default_value for d in self.__inclusive_date_range(
            start_date, end_date)}

    def __coordinates(self, location):
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

    def __inclusive_date_range(self, start_date, end_date):
        """Returns a list of date objects in the given range."""
        return([d.date() for d in list(rrule.rrule(rrule.DAILY,
            dtstart=start_date, until=end_date))])

    def set_location(self, checkout_date, nights, location):
        """ Sets the distances for the dates in a given hotel stay."""
        dates = self.__inclusive_date_range(
            first_morning(checkout_date, nights),
            checkout_date)
        
        for day in dates:
            if day in self.locations.keys():
                self.locations[day] = {
                    'city': location,
                    'coordinates': self.__coordinates(location)}
    
    