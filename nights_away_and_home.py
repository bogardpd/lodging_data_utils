"""
This script generates a graphical representation of nights away and home
from hotel log data.
"""

from modules.collections import GroupedStayCollection
from modules.svg_chart import SVGChart

from datetime import date
from pathlib import Path

import argparse

def nights_away_and_home(output_file, start_date=None, thru_date=None):
    """Main function to generate nights away and home chart."""
    
    gsc = GroupedStayCollection(start_date, thru_date)

    svg = SVGChart(gsc)
    svg.export(output_file)
    
    return
    ####################################################################

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
    parser.add_argument('--start',
        help="The first morning to include in the chart (YYYY-MM-DD).",
        type=date.fromisoformat,
    )
    parser.add_argument('--thru',
        help="The last morning to include in the chart (YYYY-MM-DD).",
        type=date.fromisoformat,
    )
    args = parser.parse_args()

    nights_away_and_home(
        args.output,
        start_date=args.start,
        thru_date=args.thru
    )