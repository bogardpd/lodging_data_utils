import yaml
from datetime import date

from modules.collections import GroupedStayCollection
from modules.common import checkin_date
from modules.hotel_data_frame import HotelDataFrame
from modules.svg_chart import SVGChart

OUTPUT_FILE_PATH = 'output/nights_away_and_home.yaml'
OUTPUT_SVG_PATH = 'output/nights_away_and_home.svg'
START_DATE = date(2009,2,10)
END_DATE = date.today()

# TODO: Add to README

hotel_df = HotelDataFrame(['Purpose'])
away_home_rows = GroupedStayCollection(hotel_df).rows()
# TODO: Filter by start and end date

# Write to file:
with open(OUTPUT_FILE_PATH, 'w', encoding="utf-8") as f:
    yaml.Dumper.ignore_aliases = lambda *args : True # Avoid references
    yaml.dump(away_home_rows, f, allow_unicode=True, sort_keys=False)

# Create SVG:
svg = SVGChart(away_home_rows)
svg.export(OUTPUT_SVG_PATH)