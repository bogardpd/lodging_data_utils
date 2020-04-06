import json, operator
from datetime import date, timedelta
from dateutil import rrule
from functools import reduce


class DateDistanceCollection:
    """Manages a range of dates with a distance assigned to each."""
    
    COORDINATES_PATH = "coordinates.json"

    def __init__(self, start_year, end_year, home_location):
        """Initialize a DateDistanceCollection."""
        
        with open(self.COORDINATES_PATH) as f:
            self.location_coordinates = json.load(f)
         
        self.home = home_location
        self.home_coordinates = self.__coordinates(self.home)

        # Create dictionary of dates with distance set to 0 by default:
        start_date = date(start_year, 1, 1)
        end_date = date(end_year, 12, 31)
        self.distances = {d:0 for d in self.__inclusive_date_range(
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
        
    def __home_distance(self, location):
        """Returns the distance from home to the provided location."""
        return 1000 # PLACEHOLDER

    def __inclusive_date_range(self, start_date, end_date):
        """Returns a list of date objects in the given range."""
        return([d.date() for d in list(rrule.rrule(rrule.DAILY,
            dtstart=start_date, until=end_date))])

    def set_distance(self, checkout_date, nights, location):
        """ Sets the distances for the dates in a given hotel stay."""
        dates = self.__inclusive_date_range(
            checkout_date - timedelta(days=(nights-1)),
            checkout_date)
        for day in dates:
            if day in self.distances.keys():
                self.distances[day] = self.__home_distance(location)
    
    