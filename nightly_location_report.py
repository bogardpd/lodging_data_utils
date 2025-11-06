"""Creates an HTML table of homes and stays by night."""

# Standard library imports
from pathlib import Path
from datetime import datetime, timedelta
from typing import cast

# Third-party imports
import argparse
from tinyhtml import html, h
import pandas as pd

# First-party imports
from lodging_data_utils import LodgingLog

def nightly_location_report(output_html_path):
    """Creates an HTML table of homes and stays by night."""

    log = LodgingLog()
    homes = log.home_locations()
    stay_mornings = log.mornings()

    # Build locations table.
    locations = log.geodata_cache['stay_locations']
    cities = log.geodata_cache['cities'][['key']]
    cities = cities.rename(columns={'key': "city_key"})
    loc_data = locations.join(cities, on='city_fid', how='left')
    loc_data = loc_data[['name', 'type', 'city_key']]

    # Calculate date range.
    min_home = homes['move_in_date'].min().date()
    max_home = homes['move_in_date'].max().date() + timedelta(days=1)
    min_stay = stay_mornings.index.min().date() - timedelta(days=1)
    max_stay = stay_mornings.index.max().date()
    min_day = min([min_home, min_stay])
    max_day = max([max_home, max_stay, datetime.now().date()])
    day_range = pd.date_range(min_day, max_day, freq='D')
    loc_df = pd.DataFrame(index=day_range)

    # Populate home fids.
    homes_indexed = homes.set_index('move_in_date')[['stay_location_fid']]
    loc_df = loc_df.merge(
        homes_indexed,
        left_index=True,
        right_index=True,
        how='left',
        sort=True,
        suffixes=(None, '_home')
    )
    loc_df['home_location_fid'] = loc_df['stay_location_fid'].ffill()
    loc_df = loc_df.drop(columns=['stay_location_fid'])

    # Populate stay fids.
    stay_evenings = stay_mornings[['stay_fid', 'stay_location_fid']]
    stay_evenings_index = cast(pd.DatetimeIndex, stay_evenings.index)
    stay_evenings.index = stay_evenings_index - pd.Timedelta(days=1)
    loc_df = loc_df.merge(
        stay_evenings,
        left_index=True,
        right_index=True,
        how='left',
        sort=True,
        suffixes=(None, '_stays')
    )

    # Join location info.
    for col in ['home_location_fid', 'stay_fid', 'stay_location_fid']:
        loc_df[col] = loc_df[col].astype('Int64')
    loc_df = loc_df.join(loc_data, on='home_location_fid', how='left')
    loc_df = loc_df.rename(columns={
        'name':     'home_name',
        'type':     'home_type',
        'city_key': 'home_city_key',
    })
    loc_df = loc_df.join(loc_data, on='stay_location_fid', how='left')
    loc_df = loc_df.rename(columns={
        'name':     'stay_name',
        'type':     'stay_type',
        'city_key': 'stay_city_key',
    })

    # Build HTML.
    h_rows = []
    for i, day in enumerate(day_range):
        if i == 0:
            first_locs = [h('td')("-"), h('td')("-")]
        else:
            first_locs = [None]
        h_rows.append(
            h('tr')(
                h('td', rowspan=2)(
                    datetime.strftime(day, "%A"),
                    h('br'),
                    datetime.strftime(day, "%Y-%m-%d"),
                ),
                *first_locs,
            )
        )
        if i == len(day_range) - 1:
            second_rowspan = 1
        else:
            second_rowspan = 2
        if pd.isna(loc_df.loc[day, 'stay_fid']):
            stay_data = []
            stay_class = "empty"
        else:
            stay_data = [
                h('span', class_="city")(str(loc_df.loc[day, 'stay_city_key'])),
                h('br'),
                loc_df.loc[day, 'stay_name'],
            ]
            stay_class = None
        h_rows.append(
            h('tr')(
                h('td', rowspan=second_rowspan)(
                    h('span', class_="city")(
                        str(loc_df.loc[day, 'home_city_key'])
                    ),
                    h('br'),
                    str(loc_df.loc[day, 'home_name']),
                ),
                h('td', rowspan=second_rowspan, class_=stay_class)(
                    *stay_data,
                )
            )
        )

    h_table = h('table')(
        h('thead')(
            h('th')("Day"),
            h('th')("Home"),
            h('th')("Stay")
        ),
        *h_rows,
    )

    output = html(lang="en")(
        h("head")(
            h("meta", charset="utf-8"),
            h("title")("Location Report"),
            h("style")("""
body {
    font-family: system-ui;
}
td {
    background-color: #cccccc;
    border: 1px solid #ffffff;
    padding: 0 0.25em;
}
td.empty {
    background-color: #eeeeee;
}
span.city {
    font-weight: 600;
}
            """)
        ),
        h("body")(
            h("h1")("Location Report"),
            h_table,
        ),
    )

    with open(output_html_path, 'w', encoding='utf-8') as file:
        file.write(output.render())
    print(f"Saved HTML to {output_html_path}")



if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Create an HTML table of homes and stays"
    )
    parser.add_argument("output_html",
        help="Output HTML file",
        type=Path,
    )
    args = parser.parse_args()
    nightly_location_report(args.output_html)
