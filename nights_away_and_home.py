"""
This script generates a graphical representation of nights away and home
from hotel log data.
"""

from modules.collections import GroupedStayCollection
from modules.svg_chart import SVGChart

from datetime import date
from pathlib import Path

import argparse

def nights_away_and_home(
    output_file, stats_output_file, start_date=None, thru_date=None
):
    """Main function to generate nights away and home chart."""
    
    gsc = GroupedStayCollection(start_date, thru_date)

    svg = SVGChart(gsc)
    svg.export(output_file)

    if stats_output_file is not None:
        with open(stats_output_file, 'w', encoding="utf-8") as f:
            f.write(
                f"Statistics for stays from {gsc.start_date} to "
                f"{gsc.thru_date}:\n\n")
            f.write("Top longest home stays:\n")
            for i, stay in enumerate(gsc.top("home")):
                f.write(f"  #{i + 1}\t{stay}\n")
            f.write("\nTop longest away stays:\n")
            for i, stay in enumerate(gsc.top("away")):
                f.write(f"  #{i + 1}\t{stay}\n")
        print(f"Wrote statistics to {stats_output_file}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Generate a chart of nights away and home."
    )
    parser.add_argument('--output',
        help="Path to save the output SVG file.",
        type=Path,
        required=True,
    )
    parser.add_argument('--stats_output',
        help="Path to save the statistics TXT file.",
        type=Path,
        default=None,
    )
    parser.add_argument('--start',
        help="The first evening to include in the chart (YYYY-MM-DD).",
        type=date.fromisoformat,
    )
    parser.add_argument('--thru',
        help="The last morning to include in the chart (YYYY-MM-DD).",
        type=date.fromisoformat,
    )
    args = parser.parse_args()

    nights_away_and_home(
        args.output,
        args.stats_output,
        start_date=args.start,
        thru_date=args.thru
    )