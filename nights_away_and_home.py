"""
This script generates a graphical representation of nights away and home
from hotel log data.
"""

from modules.collections import GroupedStayCollection
from modules.hotel_data_frame import HotelDataFrame
from modules.svg_chart import SVGChart

from datetime import date
from pathlib import Path

import argparse

def nights_away_and_home(output_file):
    """Main function to generate nights away and home chart."""

    START_DATE = date(2009,2,9)
    END_DATE = date.today()

    hotel_df = HotelDataFrame(['Purpose'])
    away_home_rows = GroupedStayCollection(hotel_df).rows()
    away_home_rows = list(filter(lambda r: r['away'].start >= START_DATE,
        away_home_rows))

    # Create SVG:
    svg = SVGChart(away_home_rows, START_DATE, END_DATE)
    svg.export(output_file)

    # Show statistics:
    current_home_nights = away_home_rows[-1]['home'].nights

    equal_or_longer_home_stays = list(filter(
        lambda r: r['home'].nights >= current_home_nights, away_home_rows[:-1]
    ))

    sorted_longer_stays = sorted(list(filter(
        lambda r: r['home'].nights > current_home_nights, away_home_rows[:-1]
    )), key=lambda s:s['home'].nights, reverse=True)
    top_stays = sorted_longer_stays + [away_home_rows[-1]]

    STATS_PATH = output_file.with_suffix('.txt')
    with open(STATS_PATH, 'w', encoding="utf-8") as f:
        if len(equal_or_longer_home_stays) == 0:
            f.write("The current home stay is the longest home stay.")
        else:
            f.write("Current home stay:\n")
            f.write(f"  {away_home_rows[-1]['home']}\n")
            f.write("\n")
            
            most_recent_eq_or_longer = equal_or_longer_home_stays[-1]['home']
            f.write("Most recent equal or longer home stay:\n")
            f.write(f"  {most_recent_eq_or_longer}\n")
            f.write("\n")

            f.write("Top longest home stays:\n")
            for i, stay in enumerate(top_stays):
                f.write(f"  #{i + 1}\t{stay['home']}\n")
    print(f"Wrote statistics to {STATS_PATH}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Generate a chart of nights away and home."
    )
    parser.add_argument('--output',
        help="Path to save the output SVG file.",
        type=Path,
        required=True,
    )
    args = parser.parse_args()

    nights_away_and_home(args.output)