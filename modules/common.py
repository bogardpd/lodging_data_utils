"""Contains common hotel data manipulation methods."""

from datetime import timedelta
from dateutil import rrule

def checkin_date(checkout_date, nights):
    """Returns the checkin date."""
    return(checkout_date - timedelta(days=nights))

def first_morning(checkout_date, nights):
    """Returns the date one day after checkin."""
    return(checkout_date - timedelta(days=(nights-1)))

def inclusive_date_range(start_date, end_date):
    """Returns a list of date objects in the given range."""
    return([d.date() for d in list(rrule.rrule(rrule.DAILY,
        dtstart=start_date, until=end_date))])

def stay_mornings(start_date, end_date):
    """Returns a list of morning dates in a given stay range.
    
    The start date is excluded from this list.
    """
    return(inclusive_date_range(start_date, end_date)[1:])