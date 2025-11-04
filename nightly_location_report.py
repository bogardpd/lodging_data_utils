"""Creates an HTML table of homes and stays by night."""

# Standard library imports
from pathlib import Path
from datetime import datetime, timedelta
from typing import cast

# Third-party imports
import argparse
import htmlgenerator as hg
import pandas as pd

# First-party imports
from lodging_data_utils import LodgingLog

def nightly_location_report(output_html_path):
    """Creates an HTML table of homes and stays by night."""

    log = LodgingLog()
    homes = log.home_locations()
    stay_mornings = log.mornings()

    min_home = homes['move_in_date'].min().date()
    max_home = homes['move_in_date'].max().date() + timedelta(days=1)

    min_day = min([min_home])
    max_day = max([max_home, datetime.now().date()])
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


    for col in ['home_location_fid', 'stay_fid', 'stay_location_fid']:
        loc_df[col] = loc_df[col].astype('Int64')

    h_rows = []
    for i, day in enumerate(day_range):
        if i == 0:
            first_locs = [hg.TD("-"), hg.TD("-")]
        else:
            first_locs = [None]
        h_rows.append(
            hg.TR(
                hg.TD(
                    datetime.strftime(day, "%a %d %b %Y"),
                    rowspan=2,
                ),
                *first_locs,
            )
        )
        if i == len(day_range) - 1:
            second_rowspan = 1
        else:
            second_rowspan = 2
        if pd.isna(loc_df.loc[day, 'stay_fid']):
            stay_str = None
        else:
            stay_str = (
                f"{loc_df.loc[day, 'stay_fid']} "
                f"{loc_df.loc[day, 'stay_location_fid']}"
            )
        h_rows.append(
            hg.TR(
                hg.TD(
                    loc_df.loc[day, 'home_location_fid'],
                    rowspan=second_rowspan,
                ),
                hg.TD(
                    stay_str,
                    rowspan=second_rowspan,
                )
            )
        )
    h_table = hg.TABLE(
        hg.THEAD(
            hg.TH("Day"),
            hg.TH("Home"),
            hg.TH("Stay")
        ),
        *h_rows,
        border=1,
    )

    output = hg.HTML(
        hg.HEAD(
            hg.TITLE("Location Report")
        ),
        hg.BODY(
            hg.H1("Location Report"),
            h_table,
        ),
        doctype=True
    )
    with open(output_html_path, 'w', encoding='utf-8') as file:
        file.write(hg.render(output, {}))
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
