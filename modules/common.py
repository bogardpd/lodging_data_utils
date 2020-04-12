"""Contains common hotel data manipulation methods."""

from datetime import timedelta

def checkin_date(checkout_date, nights):
    """Returns the checkin date."""
    return(checkout_date - timedelta(days=nights))

def first_morning(checkout_date, nights):
    """Returns the date one day after checkin."""
    return(checkout_date - timedelta(days=(nights-1)))