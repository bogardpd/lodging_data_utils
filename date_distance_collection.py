import datetime
from dateutil import rrule

class DateDistanceCollection:
    """Manages a range of dates with a distance assigned to each."""

    def __init__(self, start_year, end_year):
        """Initialize a DateDistances instance."""
        start_date = datetime.date(start_year, 1, 1)
        end_date = datetime.date(end_year, 12, 31)

        self.distances = {
            d.date():0 for d in list(
                rrule.rrule(
                    rrule.DAILY,
                    dtstart=start_date,
                    until=end_date))}
        
    def set_distance(self, checkout_date, nights, distance):
        """ Sets the distances for the dates in a given hotel stay."""