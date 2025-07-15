"""
Creates a table of lodging locations and the number of nights spent at
each location, grouped by location, city, metro area, or region.
"""

# Standard library imports
import datetime
from pathlib import Path

# Third-party imports
import argparse

# First-party imports
from lodging_data_utils import LodgingLog

COORD_DECIMALS = 4  # Number of decimal places for coordinates

def frequency_table(
    by='City',
    start_morning=None,
    thru_morning=None,
    output_csv=None,
    top=None,
    exclude_transit=False,
    rank=False,
    silent=False,
):
    """Create a frequency table of hotel locations and nights."""

    log = LodgingLog()

    mornings = log.mornings_by(
        by=by,
        start_morning=start_morning,
        thru_morning=thru_morning,
        exclude_transit=exclude_transit,
    )

    # Group and count the nights by location.
    grouped = mornings.groupby('type_fid').agg(
        title=('title', 'first'),
        name=('name', 'first'),
        key=('key', 'first'),
        place_type=('place_type', 'first'),
        latitude=('lat', 'first'),
        longitude=('lon', 'first'),
        night_count=('type_fid', 'count'),
    )
    grouped = grouped.sort_values(
        by=['night_count','name'],
        ascending=[False, True],
    )

    # Round coordinates to a fixed number of decimal places.
    grouped['latitude'] = grouped['latitude'].round(COORD_DECIMALS)
    grouped['longitude'] = grouped['longitude'].round(COORD_DECIMALS)

    # Remove title if not needed.
    grouped = grouped.dropna(axis=1, how='all')

    if rank:
        grouped['rank'] = grouped['night_count'] \
            .rank(method='min', ascending=False) \
            .astype('int')
        columns = grouped.columns.to_list()
        columns = columns[-1:] + columns[:-1]
        grouped = grouped[columns]

    total_nights = grouped['night_count'].sum()
    total_locs = len(grouped)
    if top is not None:
        grouped = grouped.head(top)
    if not silent:
        print(grouped.to_string(index=False))
        print(pluralize_total(by, total_locs))
        print(pluralize_total('night', total_nights))

    if output_csv is not None:
        grouped.to_csv(output_csv, index=False)
        print(f"Saved CSV to `{output_csv}`.")


def pluralize_total(label, count):
    """Return a string with the total count and label."""
    total_labels = {
        'night': ["night", "nights"],
        'region': ["region", "regions"],
        'metro': ["metro area", "metro areas"],
        'city': ["city", "cities"],
        'location': ["location", "locations"],
    }
    if count == 1:
        label_str = total_labels[label][0]
    else:
        label_str = total_labels[label][1]
    return f"Total {label_str}: {count}"


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Create a CSV of hotel locations and nights."
    )
    parser.add_argument('--by',
        help="group by `location`, `city`, `metro` or `region`",
        choices=['location','city','metro','region'],
        default='city',
    )
    parser.add_argument('--start_morning',
        help="the earliest morning to show (inclusive) in YYYY-MM-DD format",
        type=datetime.date.fromisoformat,

    )
    parser.add_argument('--thru_morning',
        help="the latest morning to show (inclusive) in YYYY-MM-DD format",
        type=datetime.date.fromisoformat,
    )
    parser.add_argument('--output_csv',
        help="CSV file to write the results to",
        type=Path
    )
    parser.add_argument('--top',
        help="how many results to show",
        type=int
    )
    parser.add_argument('--exclude_transit',
        help="do not include nights on flights",
        action='store_true',
    )
    parser.add_argument('--rank',
        help="show a ranking column",
        action='store_true'
    )
    parser.add_argument('--silent',
        help="do not show table in console",
        action='store_true'
    )
    args = parser.parse_args()
    frequency_table(
        args.by,
        start_morning=args.start_morning,
        thru_morning=args.thru_morning,
        output_csv=args.output_csv,
        top=args.top,
        exclude_transit=args.exclude_transit,
        rank=args.rank,
        silent=args.silent,
    )
