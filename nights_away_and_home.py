import yaml
from modules.common import checkin_date
from modules.hotel_data_frame import HotelDataFrame
from datetime import date

OUTPUT_FILE_PATH = 'output/nights_away_and_home.yaml'

hotel_df = HotelDataFrame()

grouped = []
previous_checkout = None
for stay in hotel_df.data.values.tolist():
    checkout = stay[0].date()
    nights = stay[1]
    city = stay[2]
    checkin = checkin_date(checkout, nights)
    
    if (len(grouped) == 0) or checkin != previous_checkout:
        # Create new group:
        
        grouped.append({
            'start': checkin,
            'end': checkout,
            'cities': [{
                'start': checkin,
                'end': checkout,
                'city': city
                }]
            })
            
    else:
        # Merge into previous group:
        
        if len(grouped[-1]['cities']) == 0 or grouped[-1]['cities'][-1]['city'] != city:
            # Create a new city:
            grouped[-1]['cities'].append({
                'start': checkin,
                'end': checkout,
                'city': city
            })
        else:
            # Merge into previous city:
            grouped[-1]['cities'][-1]['end'] = checkout

        grouped[-1]['end'] = checkout
    
    previous_checkout = checkout

with open(OUTPUT_FILE_PATH, 'w', encoding="utf-8") as f:
    yaml.dump(grouped, f, allow_unicode=True, sort_keys=False)