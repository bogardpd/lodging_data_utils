"""Creates a CSV report of regions lived or stayed in by a traveler."""

# Standard library imports
import argparse
import sqlite3

# Third party imports
import pandas as pd

# First party imports
from modules.lodging_log import LodgingLog

def create_regions_report(output_csv):
    """Creates a CSV report of regions lived or stayed in."""

    log = LodgingLog()

    # Load all regions from the lodging GeoPackage.
    lodging_path = log.lodging_path
    conn = sqlite3.connect(lodging_path)
    query = """
        SELECT fid, iso_3166, name, admin_level, parent_region_fid
        FROM regions
    """
    regions_df = pd.read_sql(query, conn, index_col="fid",
        dtype={"admin_level": "Int32", "parent_region_fid": "Int64"}
    )
    print(regions_df)
    conn.close()

    # Load homes by region.
    homes_df = log.home_locations()
    home_regions = homes_df['region_fid'].dropna().unique().tolist()
    home_regions = roll_up_regions(home_regions, regions_df)

    # Load stays by region.
    stays_df = log.mornings_by("region", exclude_transit=True)
    stays_df = stays_df[stays_df['place_type'] == 'Region']
    stays_df = stays_df[stays_df['region_fid'].notna()]
    stayed_regions = stays_df['region_fid'].unique().tolist()
    stayed_regions = roll_up_regions(stayed_regions, regions_df)

    # Create lived_in and stayed_in columns.
    regions_df['lived_in'] = regions_df.index.isin(home_regions)
    regions_df['stayed_in'] = regions_df.index.isin(stayed_regions)

    # Filter columns and sort the DataFrame.
    regions_df = regions_df[
        ['iso_3166', 'name', 'admin_level', 'lived_in', 'stayed_in']
    ]
    regions_df.sort_values(by='iso_3166', inplace=True)

    # Save the DataFrame to a CSV file.
    regions_df.to_csv(output_csv, index=False)

def roll_up_regions(fid_list, regions_df):
    """Takes a list of region FIDs and returns the list with parent
    regions included.
    """
    for fid in fid_list:
        parent_fid = regions_df.loc[fid, 'parent_region_fid']
        if pd.notna(parent_fid) and parent_fid not in fid_list:
            fid_list.append(int(parent_fid))
    return fid_list

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=(
        "Create a CSV report of regions lived or stayed in by a traveler."
    ))
    parser.add_argument("output_csv", help="Path to the output CSV file")

    args = parser.parse_args()

    create_regions_report(args.output_csv)
    print(f"Regions report created at {args.output_csv}")
