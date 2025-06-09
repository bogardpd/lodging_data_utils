"""Contains classes for creating various collections of hotel data."""

from modules.lodging_log import LodgingLog

from modules.common import first_morning
from datetime import date
import pandas as pd


class GroupedStayCollection:
    """Groups consecutive away-from-home stays.
        
        Creates a list of dictionaries of away period/home period
        pairs, with details for each in nested dictionaries.
        """
    END_DATE = date.today()

    def __init__(self, start_date=None, thru_date=None):
        """Initialize a GroupedStayCollection."""
        self.log = LodgingLog()
        self.start_date = start_date
        if self.start_date is None:
            # Use the first morning in the log as the start date.
            start_date = self.log.index.min().date()
        self.thru_date = thru_date
        if self.thru_date is None:
            # Use today as the thru date.
            self.thru_date = date.today()

        self.groups = self._group_stays()
        
    def _group_stays(self):
        """Groups consecutive away-from-home stays."""

        # Get lodging data from the log.
        lodging = self.log.mornings().copy()
        lodging['status'] = "Away"  # Default status for all stays.
        lodging = lodging[['status', 'purpose']]

        # Create a DataFrame with all mornings in the range.
        mornings = pd.DataFrame()
        mornings['morning'] = pd.date_range(
            start=self.start_date,
            end=self.thru_date,
            freq='D',
        )
        mornings = mornings.set_index('morning')
        
        # Merge the lodging data with the mornings DataFrame.
        mornings = pd.merge(
            mornings,
            lodging,
            left_index=True,
            right_index=True,
            how='left',
        )
        mornings['status'] = mornings['status'].fillna("Home")

        # Create a list of StayPeriod objects to group stays.
        grouped = []
        prev_m = None
        for m in mornings.itertuples():
            if len(grouped) == 0 or m.status != prev_m.status:
                # Create a new StayPeriod:
                if m.status == "Away":
                    grouped.append(
                        StayPeriod(True, m.Index.date(), m.purpose))
                else:
                    grouped.append(
                        StayPeriod(False, m.Index.date()))
            else:
                # Merge into previous group:
                if m.status == "Away":
                    grouped[-1].append_morning(m.purpose)
                else:
                    grouped[-1].append_morning()
            prev_m = m

        return grouped
    
    def rows(self):
        """Creates a row for each away period/home period pair.

        Calculates the length of each home stay between two away groups.
        """
        if self.groups[0].is_away:
            groups = self.groups
        else:
            # Rows must start with away. If the first group is home, add
            # a None value for the first row's Away.
            groups = [None] + self.groups
        rows = [
            {
                'away': groups[i],
                'home': groups[i + 1] if i + 1 < len(groups) else None
            }
            for i in range(0, len(groups), 2)
        ]
        return rows
    
class StayPeriod:
    """
    Contains details for a single home or away stay period.

    An away stay period may have multiple back to back hotel stays.
    """
    def __init__(self, is_away, end_date, purpose=None):
        """Initializes a StayPeriod with a single night."""
        self.is_away = is_away
        self.start_date = end_date - pd.Timedelta(days=1)
        self.end_date = end_date
        self.nights = 1
        if is_away:
            self.purposes = [purpose]
        else:
            self.purposes = []

    def __str__(self):
        """Returns a StayPeriod as a string."""
        period_type = "Away" if self.is_away else "Home"    
        return (f"{period_type} thru {self.end_date} "
                f"({self.nights} night{'s' if self.nights > 1 else ''})")
    
    def __repr__(self):
        """Returns a StayPeriod as a string."""
        period_type = "Away" if self.is_away else "Home"    
        return (f"{period_type} thru {self.end_date} "
                f"({self.nights} night{'s' if self.nights > 1 else ''})")
    
    def append_morning(self, purpose=None):
        """
        Appends a morning to the stay period. This is used to extend the stay period by one night."""
        self.nights += 1
        self.end_date = self.end_date + pd.Timedelta(days=1)
        self.start_date = self.end_date - pd.Timedelta(days=self.nights)
        if self.is_away:
            self.purposes.append(purpose)

    def date_range_string(self):
        """Returns a formatted string for the stay start and end dates.
        """
        start = self.start_date
        end = self.end_date
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
        return(first_morning(self.end_date, self.nights))
