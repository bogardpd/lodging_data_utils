"""Creates a CSV of hotel locations and nights, either by city or by
CBSA metro area."""

import argparse
import datetime
import numpy as np
import pandas as pd
import sqlite3
import tomllib
from pathlib import Path

from modules.hotel_data_frame import HotelDataFrame

with open(Path(__file__).parent / "config.toml", 'rb') as f:
    config = tomllib.load(f)
con = sqlite3.connect(Path(config['files']['location_db']).expanduser())

def frequency_table(
    by='city',
    start_date=None,
    thru_date=None,
    output_file=None,
    top=None,
    rank=False,
):
    mornings = HotelDataFrame().by_morning().loc[start_date:thru_date]
    cities_df = pd.read_sql("SELECT * FROM cities", con).set_index('city_id')
    cities_df['metro_id'] = cities_df['metro_id']
    mornings = mornings.join(cities_df, on='city')

    if by == 'metro':
        city_mornings = mornings[mornings['metro_id'].isnull()]
        metro_mornings = mornings[mornings['metro_id'].notnull()]
        
        cities_grouped = group_cities(city_mornings)
        metros_grouped = group_metros(metro_mornings)

        grouped = pd.concat([cities_grouped, metros_grouped])
        column_order = [
            'title',
            'location',
            'type',
            'metro_id',
            'latitude',
            'longitude',
            'nights',
        ]
        grouped = grouped[column_order]
    elif by == 'state':
        mornings = mornings[mornings['city'].str.match("US")]
        mornings['state'] = mornings['city'].apply(lambda x:
            str(x).split('/')[1]
        )
        grouped = group_states(mornings)
    else:
        grouped = group_cities(mornings)
    
    grouped = grouped.sort_values(
        by=['nights','location'],
        ascending=[False, True],
    )
    if rank:
        grouped['rank'] = grouped['nights'] \
            .rank(method='min', ascending=False) \
            .astype('int')
        columns = grouped.columns.to_list()
        columns = columns[-1:] + columns[:-1]
        grouped = grouped[columns]
    
    total_nights = grouped['nights'].sum()
    if top is not None:
        grouped = grouped.head(top)
    print(grouped)
    print("Total night(s):", total_nights)

    if output_file is not None:
        grouped.to_csv(output_file, index=False)
        print(f"Saved CSV to `{output_file}`.")

def group_cities(mornings):
    if mornings.empty:
        return pd.DataFrame()
    mornings = mornings.assign(type='city')
    mornings.loc[
        mornings['city'].str.startswith('FLIGHT'), 'type'
    ] = 'flight'
    grouped = mornings.groupby('city').agg(
        location=('name', 'first'),
        type=('type', 'first'),
        latitude=('latitude', 'first'),
        longitude=('longitude', 'first'),
        nights=('city', 'count'),
    )
    grouped.index.names = ['loc_id']
    return grouped

def group_metros(mornings):
    if mornings.empty:
        return pd.DataFrame()
    mornings = mornings.assign(type='metro')
    metros_df = pd.read_sql("SELECT * FROM metro_areas", con)
    metros_df = metros_df.set_index('metro_id')
    mornings = mornings.join(metros_df,
        on='metro_id',
        rsuffix='_metro'
    )
    grouped = mornings.groupby('metro_id').agg(
        title=('metro_title', 'first'),
        location=('short_name', 'first'),
        type=('type', 'first'),
        metro_id=('metro_id', 'first'),
        latitude=('latitude_metro', 'first'),
        longitude=('longitude_metro', 'first'),
        nights=('city', 'count'),
    )
    grouped['metro_id'] = grouped['metro_id'].astype('string')
    grouped.index.names = ['loc_id']
    
    return grouped

def group_states(mornings):
    if mornings.empty:
        return pd.DataFrame()
    mornings = mornings.assign(type='state')
    states_df = pd.read_sql("SELECT * FROM us_states", con)
    states_df = states_df.set_index('abbrev')
    mornings = mornings.join(states_df,
        on='state',
        rsuffix='_state'
    )
    grouped = mornings.groupby('state').agg(
        location=('name_state', 'first'),
        type=('type', 'first'),
        latitude=('latitude', 'first'),
        longitude=('longitude', 'first'),
        nights=('city', 'count'),
    )
    grouped.index.names = ['state']
    return grouped
    

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Create a CSV of hotel locations and nights."
    )
    parser.add_argument('--by',
        help="group by `city`, `metro` or `state`",
        choices=['city','metro','state'],
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
    parser.add_argument('--rank',
        help="show a ranking column",
        action='store_true'
    )
    args = parser.parse_args()
    frequency_table(
        args.by, args.start, args.thru, args.output, args.top, args.rank
    )
