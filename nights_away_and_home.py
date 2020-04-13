import yaml
from datetime import date

from modules.common import checkin_date
from modules.hotel_data_frame import HotelDataFrame

OUTPUT_FILE_PATH = 'output/nights_away_and_home.yaml'
START_DATE = date(2009,2,10)
END_DATE = date.today()

# TODO: Add to README

def group_stays(hotel_data_frame):
    """Groups consecutive away-from-home stays."""
    grouped = []
    previous_checkout = None
    for stay in hotel_df.data.values.tolist():
        checkout = stay[0].date()
        nights = stay[1]
        city = stay[2]
        checkin = checkin_date(checkout, nights)

        # TODO: Ensure checkin is before checkout
        # TODO: Ensure stays don't overlap
        # TODO: Add business/personal to stays (split same city if necessary)
        
        if (len(grouped) == 0) or checkin != previous_checkout:
            # Create new group:
            
            grouped.append({
                'start': checkin,
                'end': checkout,
                'nights': (checkout - checkin).days,
                'cities': [{
                    'city': city,
                    'start': checkin,
                    'end': checkout,
                    'nights': (checkout - checkin).days
                    }]
                })
                
        else:
            # Merge into previous group:
            grouped[-1]['end'] = checkout
            grouped[-1]['nights'] = (checkout - grouped[-1]['start']).days
            
            if len(grouped[-1]['cities']) == 0 or grouped[-1]['cities'][-1]['city'] != city:
                # Create a new city:
                grouped[-1]['cities'].append({
                    'city': city,
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

def create_rows(grouped_stays):
    """Creates a row for each away period/home period pair.

    Calculates the length of each home stay between two away groups.
    """
    away_home_rows = []
    for i, group in enumerate(grouped_stays):
        home_start = group['end']
        if i == len(grouped_stays) - 1:
            home_end = END_DATE 
        else:
            home_end = grouped_stays[i + 1]['start']
        away_nights = (group['end'] - group['start']).days
        away = group
        home = {
            'start': home_start,
            'end': home_end,
            'nights': (home_end - home_start).days
        }
        away_home_rows.append({'away': away, 'home': home})
    return(away_home_rows)


# MAIN SCRIPT:

hotel_df = HotelDataFrame(['Purpose'])
grouped = group_stays(hotel_df)
# TODO: Filter by start and end date
away_home_rows = create_rows(grouped)

# Write to file:
with open(OUTPUT_FILE_PATH, 'w', encoding="utf-8") as f:
    yaml.Dumper.ignore_aliases = lambda *args : True # Avoid references
    yaml.dump(away_home_rows, f, allow_unicode=True, sort_keys=False)