"""
A script to generate charts showing distance from home for each day of
a year. Can also include prior years and average distance across a
range of years.
"""

# Standard library imports
import csv
from pathlib import Path
from datetime import date, datetime

# Third-party imports
import argparse
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import matplotlib.ticker as ticker
import numpy as np
import pandas as pd
from matplotlib.gridspec import GridSpec
from pyproj import Geod

# First-party imports
from modules.lodging_log import LodgingLog

KM_PER_MILE = 1.6093
DECIMAL_PLACES = 2 # Number of decimal places to round distances to.

COLORS = {
    'line': "#ee7733",
    'line_prior': "#cccccc",
    'face': "#bf500c",
    'grid_major': "#d0d0d0",
    'grid_minor': "#f0f0f0",
}

def distance_from_home_by_day(
    single_multi, years,
    output_img=None, output_csv=None, labels=None, earliest_prior_year=None
):
    """
    Generate a distance from home by day chart for a single year or
    multiple years.
    """
    if single_multi == 'single':
        SingleYearDistanceChart(
            years[0],
            output_img,
            output_csv,
            labels,
            earliest_prior_year,
        ).plot()
    elif single_multi == 'multi':
        YearsAndAverageDistanceChart(years[0], years[1], output_img).plot()


class DistanceByDayChart():
    """Parent class for distance by day charts."""

    def __init__(self):
        """Initialize the chart."""
        self.log = LodgingLog()
        self.home_locations = self.log.home_locations()

    def apply_styles(self, ax, ax_data, year, include_xaxis=False):
        """
        Apply styles to the given axis for the distance by day chart.
        """
        ax.fill_between(ax_data['dates'], ax_data['distances'], 0,
            facecolor=COLORS['face'], alpha=0.1)
        ax.xaxis.set_major_locator(mdates.MonthLocator())
        ax.xaxis.set_minor_locator(mdates.MonthLocator(bymonthday=16))
        ax.xaxis.grid(True, which='major', color=COLORS['grid_major'])
        ax.xaxis.set_tick_params(length=0)
        ax.set_xlim([date(year,1,1),date(year,12,31)])
        for tick in ax.xaxis.get_minor_ticks():
            tick.tick1line.set_markersize(0)
            tick.tick2line.set_markersize(0)
            tick.label1.set_horizontalalignment('center')
        if include_xaxis:
            ax.xaxis.set_major_formatter(ticker.NullFormatter())
            ax.xaxis.set_minor_formatter(mdates.DateFormatter("%b"))
        else:
            ax.get_xaxis().set_ticklabels([])

    def date_year_distance_matrix(self, years_inclusive):
        """
        Returns a DataFrame of miles from home for each day in the
        specified inclusive range of years.
        """
        def morning_distance(morning, mornings_lodging):
            """Calculate miles from home for a given morning."""
            morning = pd.Timestamp(morning)
            if morning in mornings_lodging.index:
                # Morning is away from home.
                home_lat_lon = self.home_lat_lon(morning)
                lodging_lat_lon = mornings_lodging.loc[
                    morning, ['lat', 'lon']
                ].values.tolist()
                geod = Geod(ellps='WGS84')
                return geod.inv(
                    home_lat_lon[1], home_lat_lon[0],
                    lodging_lat_lon[1], lodging_lat_lon[0],
                )[2] / (1000 * KM_PER_MILE) # Convert meters to miles
            else:
                # Morning is at home.
                return 0.0

        # Get all lodging in the specified range of years.
        lodging_mornings = self.log.mornings_by(
            by='city',
            start_morning=date(years_inclusive[0], 1, 1),
            thru_morning=date(years_inclusive[1], 12, 31),
            exclude_transit=False,
        )

        # Create a DataFrame with all mornings in the range.
        df = pd.DataFrame()
        df['morning'] = pd.date_range(
            start=date(years_inclusive[0], 1, 1),
            end=date(years_inclusive[1], 12, 31),
            freq='D',
        )

        # Calculate distance from home for each morning.
        df['distance_mi'] = df['morning'].apply(
            lambda d: morning_distance(d, lodging_mornings)
        ).round(DECIMAL_PLACES)

        # Split out years, months, and days.
        df['year'] = df['morning'].dt.year
        df['month'] = df['morning'].dt.month
        df['day'] = df['morning'].dt.day

        # Create a pivot table with years as columns and dates as rows.
        df = df.pivot_table(
            index=['month', 'day'],
            columns='year',
            values='distance_mi',
            fill_value=np.nan,
        )
        return df

    def home_lat_lon(self, morning):
        """
        Returns the latitude and longitude of the home location for a
        given morning.
        """
        morning = pd.Timestamp(morning)
        homes = self.home_locations[
            self.home_locations['move_in_date'] < morning
        ].sort_values(by='move_in_date', ascending=False).head(1)
        if homes.empty:
            raise ValueError(f"No home location found for {morning}.")
        return [homes.iloc[0]['lat'], homes.iloc[0]['lon']]

    def normalize_year(self, year_series, year):
        """Returns a normalized year for plotting purposes."""
        ds = year_series.copy()
        # Drop February 29 if year is not a leap year.
        if year % 4 != 0 or (year % 100 == 0 and year % 400 != 0):
            ds = ds.drop((2, 29), errors='ignore')

        # Convert index to date objects.
        ds.index = ds.index.map(
            lambda d: date(year, d[0], d[1])
        )
        return ds


class SingleYearDistanceChart(DistanceByDayChart):
    """A chart showing distance by day for a single year."""

    def __init__(
            self, year,
            output_img=None, output_csv=None,
            labels=None, earliest_prior_year=None,
        ):
        super().__init__()

        self.year = int(year)
        self.output_img = output_img
        self.output_csv = output_csv

        if earliest_prior_year is not None:
            # Include prior years.
            earliest_prior_year = int(earliest_prior_year)
            if earliest_prior_year >= self.year:
                raise ValueError(
                    f"earliest_prior_year ({earliest_prior_year}) "
                    f"must be less than year ({self.year})."
                )
            years = [earliest_prior_year, self.year]
            self.prior_years = range(earliest_prior_year, self.year)
        else:
            # Do not include prior years.
            years = [self.year, self.year]
            self.prior_years = None

        self.dist_matrix = self.date_year_distance_matrix(years)
        self.labels = labels

    def plot(self):
        """
        Plot the distance by day chart.

        Note: if self.year is not a leap year, February 29 will not be
        included in the chart for any prior years.
        """
        ax = plt.subplots(1,1,figsize=(9,3),dpi=96)[1]

        # Plot prior years (if any):
        max_miles_prior = 0
        if self.prior_years is not None:
            for y in self.prior_years:
                # Normalize the year series to the current year. This is
                # necessary to ensure that the x-axis dates match.
                year_series = self.normalize_year(
                    self.dist_matrix[y], self.year
                )
                max_miles_prior = max(max_miles_prior, year_series.max())
                data = {
                    'title': str(y),
                    'dates': year_series.index,
                    'distances': year_series.values,
                }
                ax.plot(
                    data['dates'],
                    data['distances'],
                    color=COLORS['line_prior'],
                    alpha=0.4
                )

        # Plot current year.
        current_year_series = self.normalize_year(
            self.dist_matrix[self.year], self.year
        )
        data = {
            'title': str(self.year),
            'dates': current_year_series.index,
            'distances': current_year_series.values,
        }
        ax.plot(data['dates'],data['distances'], color=COLORS['line'])

        # Configure plot.
        self.apply_styles(ax, data, self.year, include_xaxis=True)
        y_max_miles = max(max_miles_prior, *list(data['distances'])) * 1.1
        y_max_km = y_max_miles * KM_PER_MILE

        ax.set_ylim(0, y_max_miles)
        ax.set_ylabel("Miles from Home")

        ax.yaxis.grid(True, which='major', color=COLORS['grid_major'])
        ax.yaxis.grid(True, which='minor', color=COLORS['grid_minor'])
        ax.yaxis.set_minor_locator(ticker.AutoMinorLocator())

        ax_km = ax.twinx()
        ax_km.set_ylim(0, y_max_km)
        ax_km.set_ylabel("Kilometers from Home")

        if self.labels is not None:
            with open(self.labels, newline='', encoding='UTF-8') as lf:
                reader = csv.DictReader(lf)
                for row in reader:
                    dt = datetime.strptime(row['morning'], "%Y-%m-%d")
                    yday = dt.date().timetuple().tm_yday - 1
                    ax.annotate(row['label'],
                        xy=(data['dates'][yday], data['distances'][yday]),
                        xycoords = 'data',
                        xytext = (15,30),
                        textcoords='offset points',
                        arrowprops = dict(
                            arrowstyle = "->",
                        )
                    )

        plt.tight_layout()

        # Export data to CSV if requested.
        if self.output_csv is not None:
            output_data = current_year_series.copy()
            output_data = output_data.reset_index()
            output_data.columns = ['morning', 'distance_mi']
            output_data.to_csv(self.output_csv, header=True, index=False)
            print(f"Saved distance data to {self.output_csv}.")

        # Show or save the plot.
        if self.output_img is None:
            plt.show()
        else:
            plt.savefig(self.output_img)
            print(f"Saved distance by day chart to {self.output_img}.")

class YearsAndAverageDistanceChart(DistanceByDayChart):
    """A chart for each year and a chart averaging all years."""

    def __init__(self, start_year, thru_year, output=None):
        super().__init__()
        self.start_year = int(start_year)
        self.thru_year = int(thru_year)
        self.output_img = output

        self.dist_matrix = self.date_year_distance_matrix(
            [self.start_year, self.thru_year]
        )

    def plot(self):
        """
        Plot a distance by day chart for each year and a chart
        averaging all years.
        """

        # Create a placeholder year to use for storing days of the year
        # when calculating mean miles for each day. Use a leap year so
        # all days are included.
        mean_data_year = 2020

        # Set plot preferences.
        year_title_options = {
            'y': 0.8,
            'verticalalignment': 'top',
            'alpha': 0.6,
            'fontsize': 10,
        }

        # Initialize the figure and grid.
        fig = plt.figure(dpi=96,figsize=(9,6))
        gs = GridSpec(12, 2, width_ratios=[1,3])

        # Create plots for each year.
        year_axs = {}
        for index, year in enumerate(range(self.start_year, self.thru_year+1)):
            year_ds = self.normalize_year(self.dist_matrix[year], year)
            data = {
                'title': str(year),
                'dates': year_ds.index,
                'distances': year_ds.values,
            }
            year_axs[index] = fig.add_subplot(gs[index, 0])
            year_axs[index].plot(data['dates'], data['distances'])
            is_bottom = index == (self.thru_year - self.start_year)
            self.apply_styles(
                year_axs[index],
                data,
                year,
                include_xaxis=is_bottom
            )
            for spine in year_axs[index].spines.values():
                spine.set_visible(False)
            year_axs[index].get_yaxis().set_visible(False)

            year_axs[index].set_xlim([date(year,1,1),date(year,12,31)])
            year_axs[index].set_ylim([-1000,12000])
            year_axs[index].set_yticks([0,6000,12000])
            year_axs[index].set_title(data['title'], **year_title_options)

            # Hide leftmost gridline for all years.
            year_axs[index].get_xgridlines()[0].set_visible(False)

            # Add month labels to the bottom year.
            if is_bottom:
                month_letters = list("JFMAMJJASOND")
                mid_months = [
                    date(year, m, 15) for m in range(1, 13)
                ]
                year_axs[index].set_xticks(
                    mid_months, month_letters, minor=True
                )

        # Plot mean distance data.
        self.dist_matrix['mean'] = (
            self.dist_matrix.mean(axis=1).round(DECIMAL_PLACES)
        )
        mean_ds = self.normalize_year(self.dist_matrix['mean'], mean_data_year)
        mean_dist_data = {
            'title': (f"Average Distance From Home by Day of Year "
                f"({self.start_year}–{self.thru_year})"),
            'dates': mean_ds.index,
            'distances': mean_ds.values,
        }
        mean_ax = fig.add_subplot(gs[:, 1])
        mean_ax.plot(mean_dist_data['dates'], mean_dist_data['distances'])
        self.apply_styles(mean_ax, data, mean_data_year, include_xaxis=True)
        mean_ax.set_title(mean_dist_data['title'])

        # Configure y-axes for mean distance plot.
        y_max_miles = 3000
        y_max_km = y_max_miles * KM_PER_MILE
        mean_ax.set_ylim(0, y_max_miles)
        mean_ax.set_ylabel("Distance (miles)")
        mean_ax_km = mean_ax.twinx()
        mean_ax_km.set_ylim(0, y_max_km)
        mean_ax_km.set_ylabel("Distance (km)")

        fig.tight_layout()
        if self.output_img is None:
            plt.show()
        else:
            plt.savefig(self.output_img)
            print(f"Saved distance by day chart to {self.output_img}.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest='single_multi', required=True)

    parser_single = subparsers.add_parser(
        'single',
        help="Create a chart for a single year.",
    )
    parser_single.add_argument(
        '--year',
        dest='year',
        type=int,
        required=True,
        help="Year to generate chart for"
    )
    parser_single.add_argument(
        '--labels',
        dest='labels',
        type=Path,
        help="CSV file of morning,label pairs",
        required=False,
        default=None
    )
    parser_single.add_argument(
        '--output_img',
        dest='output_img',
        type=Path,
        help="Output image file",
        default=None,
    )
    parser_single.add_argument(
        '--output_csv',
        dest='output_csv',
        type=Path,
        help="Output CSV file with distance data",
        default=None,
    )
    parser_single.add_argument(
        '--earliest_prior_year',
        dest='earliest_prior_year',
        type=int,
        help="Include lines for prior years back through this year",
        default=None
    )

    parser_multi = subparsers.add_parser(
        'multi',
        help=(
            "Create charts for a range of years and a chart of all years "
            "averaged."
        )
    )
    parser_multi.add_argument(
        '--start_year',
        dest='start_year',
        type=int,
        help="First year to include in the chart",
    )
    parser_multi.add_argument(
        '--thru_year',
        dest='thru_year',
        type=int,
        help="Last year to include in the chart",
    )
    parser_multi.add_argument(
        '--output_img',
        dest='output_img',
        type=Path,
        help="Output image file",
        default=None,
    )

    args = parser.parse_args()
    if args.single_multi == 'single':
        distance_from_home_by_day(
            'single',
            [args.year],
            args.output_img,
            args.output_csv,
            args.labels,
            args.earliest_prior_year,
        )
    else:
        distance_from_home_by_day(
            'multi',
            [args.start_year, args.thru_year],
            args.output_img
        )
