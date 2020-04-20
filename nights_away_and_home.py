import yaml
from datetime import date

from modules.collections import GroupedStayCollection
from modules.common import checkin_date
from modules.hotel_data_frame import HotelDataFrame
from modules.svg_chart import SVGChart

OUTPUT_FILE_PATH = "output/nights_away_and_home.yaml"
OUTPUT_STATISTICS_PATH = "output/Nights Away and Home Stats.txt"
OUTPUT_SVG_PATH = "output/Nights Away and Home.svg"
START_DATE = date(2009,2,9)
END_DATE = date.today()

hotel_df = HotelDataFrame(['Purpose'])
away_home_rows = GroupedStayCollection(hotel_df).rows()
away_home_rows = list(filter(lambda r: r['away'].start >= START_DATE,
    away_home_rows))

# # Write to file:
# with open(OUTPUT_FILE_PATH, 'w', encoding="utf-8") as f:
#     yaml.Dumper.ignore_aliases = lambda *args : True # Avoid references
#     yaml.dump(away_home_rows, f, allow_unicode=True, sort_keys=False)

# Create SVG:
svg = SVGChart(away_home_rows, START_DATE, END_DATE)
svg.export(OUTPUT_SVG_PATH)

# Show statistics:
current_home_nights = away_home_rows[-1]['home'].nights

equal_or_longer_home_stays = list(filter(
    lambda r: r['home'].nights >= current_home_nights, away_home_rows[:-1]
))

sorted_longer_stays = sorted(list(filter(
    lambda r: r['home'].nights > current_home_nights, away_home_rows[:-1]
)), key=lambda s:s['home'].nights, reverse=True)
top_stays = sorted_longer_stays + [away_home_rows[-1]]

with open(OUTPUT_STATISTICS_PATH, 'w', encoding="utf-8") as f:
    if len(equal_or_longer_home_stays) == 0:
        f.write("The current home stay is the longest home stay.")
    else:
        f.write("Current home stay:\n")
        f.write(f"  {away_home_rows[-1]['home']}\n")
        f.write("\n")
        
        most_recent_equal_or_longer = equal_or_longer_home_stays[-1]['home']
        f.write("Most recent equal or longer home stay:\n")
        f.write(f"  {most_recent_equal_or_longer}\n")
        f.write("\n")

        f.write("Top longest home stays:\n")
        for i, stay in enumerate(top_stays):
            f.write(f"  #{i + 1}\t{stay['home']}\n")