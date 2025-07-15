"""Create a CSV file with night counts for each year in the dataset."""

# Standard library imports
from datetime import date
from pathlib import Path
from typing import cast

# Third-party imports
import argparse
import pandas as pd

# First-party imports
from lodging_data_utils import LodgingLog

def create_annual_night_counts(output_csv: Path) -> None:
    """Create a CSV file with night counts for each year in the dataset."""
    # Get lodging log data.
    log = LodgingLog()
    mornings = log.mornings()
    mornings['year'] = cast(pd.DatetimeIndex, mornings.index).year
    mornings = mornings[['year', 'purpose']].reset_index()

    # Create a pivot table for year and purpose counts.
    annual_counts = pd.pivot_table(mornings,
        index='year',
        columns='purpose',
        values='morning',
        aggfunc='count',
        fill_value=0,
    )

    # Create a date range from the minimum year to the current year.
    # This ensures that all years are represented in the output, even if
    # there are no entries for some years.
    year_range = range(mornings['year'].min(), date.today().year + 1)
    all_annual_counts = pd.DataFrame(year_range, columns=['year'])

    # Merge the date DataFrame with the annual counts
    all_annual_counts = all_annual_counts.merge(
        annual_counts,
        on='year',
        how='left'
    ).fillna(0)
    all_annual_counts.rename(columns={
        'Business': 'business_night_count',
        'Personal': 'personal_night_count',
    }, inplace=True)
    all_annual_counts = all_annual_counts.astype({
        'business_night_count': 'int', 'personal_night_count': 'int'
    })

    # Save the result to a CSV file.
    all_annual_counts.to_csv(output_csv, index=False)
    print(f"Annual night counts saved to {output_csv}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Create a CSV file with annual night counts."
    )
    parser.add_argument('output_csv',
        type=Path,
        help="Path to the output CSV file for annual night counts."
    )
    args = parser.parse_args()
    create_annual_night_counts(args.output_csv)
