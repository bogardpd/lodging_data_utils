"""Creates a CSV of hotel locations and nights, either by city or by
CBSA metro area."""

import argparse
import datetime
import numpy as np
import pandas as pd
from pathlib import Path

from modules.coordinates import CITIES_PATH, METROS_PATH
from modules.hotel_data_frame import HotelDataFrame

def frequency_table(
    by='city', start_date=None, thru_date=None, output_file=None
):
    mornings = HotelDataFrame().by_morning().loc[start_date:thru_date]
    cities_df = pd.read_csv(CITIES_PATH,
        index_col='city',
        dtype={'metro_id': 'string'}
    )
    mornings = mornings.join(cities_df, on='city')
    
    if by == 'metro':
        grouped = group_by_metro(mornings)
    else:
        grouped = group_by_city(mornings)
        
    print(grouped)
    if output_file is not None:
        grouped.to_csv(output_file, index=False)
        print(f"Saved CSV to `{output_file}`.")

def group_by_city(mornings):
    mornings['name'] = mornings.apply(lambda x:
        str(x['city']).split("/")[-1],
        axis=1
    )
    mornings['type'] = "City"
    grouped = mornings.groupby('city').agg({
        'name': 'first',
        'type': 'first',
        'latitude': 'first',
        'longitude': 'first',
        'city': 'count',
    })
    grouped = grouped.rename(columns={'city': 'nights'})
    grouped = grouped.sort_values('nights', ascending=False)
    return grouped

def group_by_metro(mornings):
    metros_df = pd.read_csv(METROS_PATH, index_col='metro_id')
    mornings = mornings.join(metros_df,
        on='metro_id',
        rsuffix='_metro'
    )
    mornings = mornings.rename(columns={
        'latitude': 'latitude_city',
        'longitude': 'longitude_city',
    })
    metro_val_cols = ['type','location','name','latitude','longitude']
    mornings[metro_val_cols] = mornings.apply(lambda x:
        metro_values(x), axis=1, result_type='expand'
    )
    grouped = mornings.groupby('location').agg({
        'name': 'first',
        'type': 'first',
        'metro_id': 'first',
        'latitude': 'first',
        'longitude': 'first',
        'location': 'count',
    })
    grouped = grouped.rename(columns={'location': 'nights'})
    grouped = grouped.sort_values('nights', ascending=False)
    return grouped

def metro_values(row):
    if pd.isnull(row['metro_id']):
        loc_type = 'city'
        location = f"city:{row['city']}"
        name = row['city'].split("/")[-1]
        lat = row['latitude_city']
        lon = row['longitude_city']
    else:
        loc_type = 'metro'
        location = f"metro:{row['metro_id']}"
        name = row['short_name']
        lat = row['latitude_metro']
        lon = row['longitude_metro']
    return [loc_type, location, name, lat, lon]

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Create a CSV of hotel locations and nights."
    )
    parser.add_argument('--by',
        help="group by `city` or `metro`",
        choices=['city','metro'],
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
    args = parser.parse_args()
    frequency_table(args.by, args.start, args.thru, args.output)
