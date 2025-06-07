"""Creates a CSV of hotel locations and nights, either by city or by
CBSA metro area."""

import argparse
import datetime
import pandas as pd
from pathlib import Path

from modules.lodging_log import LodgingLog

def frequency_table(
    by='City',
    start_date=None,
    thru_date=None,
    output_file=None,
    top=None,
    exclude_flights=False,
    rank=False,
    silent=False,
):
    """Create a frequency table of hotel locations and nights."""
    
    log = LodgingLog()
    
    mornings = log.mornings_by(
        by=by,
        start_date=start_date,
        thru_date=thru_date,
        exclude_flights=exclude_flights,
    )

    # Group and count the nights by location.
    grouped = mornings.groupby('type_fid').agg(
        Location=('name', 'first'),
        Title=('title', 'first'),
        LocId=('key', 'first'),
        Type=('loc_type', 'first'),
        Latitude=('lat', 'first'),
        Longitude=('lon', 'first'),
        Nights=('type_fid', 'count'),
    )
    grouped = grouped.sort_values(
        by=['Nights','Location'],
        ascending=[False, True],
    )
    
    # Remove Title or LocId if not needed.
    grouped = grouped.dropna(axis=1, how='all')
   
    if rank:
        grouped['Rank'] = grouped['Nights'] \
            .rank(method='min', ascending=False) \
            .astype('int')
        columns = grouped.columns.to_list()
        columns = columns[-1:] + columns[:-1]
        grouped = grouped[columns]
    
    total_nights = grouped['Nights'].sum()
    total_locs = len(grouped)
    if top is not None:
        grouped = grouped.head(top)
    if not silent:
        print(grouped.to_string(index=False))
        print(pluralize_total(by, total_locs))
        print(pluralize_total('night', total_nights))

    if output_file is not None:
        grouped.to_csv(output_file, index=False)
        print(f"Saved CSV to `{output_file}`.")
        

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
    parser.add_argument('--start',
        help="the earliest morning to show (inclusive) in YYYY-MM-DD format",
        type=datetime.date.fromisoformat,
        
    )
    parser.add_argument('--thru',
        help="the latest morning to show (inclusive) in YYYY-MM-DD format",
        type=datetime.date.fromisoformat,
    )
    parser.add_argument('--output',
        help="CSV file to write the results to",
        type=Path
    )
    parser.add_argument('--top',
        help="how many results to show",
        type=int
    )
    parser.add_argument('--exclude_flights',
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
        args.by, args.start, args.thru, args.output, args.top,
        args.exclude_flights, args.rank, args.silent,
    )
