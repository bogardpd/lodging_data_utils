from modules.collections import DateCollection
from modules.hotel_data_frame import HotelDataFrame

import argparse
from datetime import date
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import matplotlib.ticker as ticker
from matplotlib.gridspec import GridSpec
from pathlib import Path
import tomllib
import numpy as np

with open(Path(__file__).parent / "config.toml", 'rb') as f:
    config = tomllib.load(f)

KM_PER_MILE = 1.609

def main(type, years, output=None):
    if type == 'single':
        SingleYearDistanceChart(years[0], output).plot()
    elif type == 'multi':
        YearsAndAverageDistanceChart(*years, output).plot()
    

class DistanceByDayChart():
    """Parent class for distance by day charts."""

    def __init__(self):
        pass

    def apply_styles(self, ax, ax_data, year, include_xaxis=False):
        ax.fill_between(ax_data['dates'], ax_data['distances'], 0,
            facecolor='blue', alpha=0.1)
        ax.xaxis.set_major_locator(mdates.MonthLocator())
        ax.xaxis.set_minor_locator(mdates.MonthLocator(bymonthday=16))
        ax.xaxis.grid(alpha=0.5)
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

class SingleYearDistanceChart(DistanceByDayChart):
    """A chart showing distance by day for a single year."""

    def __init__(self, year, output=None):
        super().__init__()
        self.year = int(year)
        self.output = output
        self.locations = DateCollection(
            HotelDataFrame(),
            date(self.year,1,1),
            date(self.year,12,31),
            config['home_location'],
        )

    def plot(self):
        distances = self.locations.distances()
        data = {
            'title': str(self.year),
            'dates': list(distances.keys()),
            'distances': list(distances.values()),
        }
        fig, ax = plt.subplots(1,1,figsize=(9,3),dpi=96)
        ax.plot(data['dates'],data['distances'])
        self.apply_styles(ax, data, self.year, include_xaxis=True)
        # ax.set_title(f"Distance from Home ({self.year})")
        y_max_miles = max(data['distances']) * 1.1
        y_max_km = y_max_miles * KM_PER_MILE

        ax.set_ylim([0,y_max_miles])
        ax.set_ylabel("Distance (miles)")

        ax_km = ax.twinx()
        ax_km.set_ylim([0,y_max_km])
        ax_km.set_ylabel("Distance (km)")

        location_dates = {
            # date(2020,3,9): "Denver",
            # date(2020,3,12): "Travel Restrictions Start",
        }

        for loc_date, city in location_dates.items():
            day = loc_date.timetuple().tm_yday
            ax.annotate(city,
                xy=(data['dates'][day], data['distances'][day]),
                xycoords = 'data',
                xytext = (15,30),
                textcoords='offset points',
                arrowprops = dict(
                    arrowstyle = "->",
                )
            )

        plt.tight_layout()
        if self.output is None:
            plt.show()
        else:
            plt.savefig(self.output)
            print(f"Saved distance by day chart to {self.output}.")

class YearsAndAverageDistanceChart(DistanceByDayChart):
    """A chart for each year and a chart averaging all years."""

    def __init__(self, start_year, end_year, output=None):
        super().__init__()
        self.start_year = start_year
        self.end_year = end_year
        self.output = output
        locations = DateCollection(
            HotelDataFrame(),
            date(self.start_year,1,1),
            date(self.end_year,12,31),
            config['home_location'],
        )
        self.by_year_data = {}
        self.days_of_year = {}
        for this_date, distance in locations.distances().items():
            # Store distance for each day in its year's dictionary.    
            if this_date.year not in self.by_year_data:
                self.by_year_data[this_date.year] = {
                    'title': str(this_date.year),
                    'dates': [],
                    'distances': [],
                }
            self.by_year_data[this_date.year]['dates'].append(this_date)
            self.by_year_data[this_date.year]['distances'].append(distance)

            # Store distance in day of year for calculating averages.
            if this_date.month not in self.days_of_year:
                self.days_of_year[this_date.month] = {}
            if this_date.day not in self.days_of_year[this_date.month]:
                self.days_of_year[this_date.month][this_date.day] = []
            self.days_of_year[this_date.month][this_date.day].append(distance)

    def plot(self):
        # Create a placeholder year to use for storing days of the year
        # when calculating averages for each day. Should be a leap year
        # so all days are included. 
        avg_year = 2020

        # Calculate averages.
        average_distance_data = {
            'title': (f"Average Distance From Home by Day of Year "
                f"({self.start_year}–{self.end_year})"),
            'dates': [],
            'distances': [],
        }
        for month, days in self.days_of_year.items():
            for day, distances in days.items():
                average_distance_data['dates'].append(date(avg_year, month, day))
                average_distance_data['distances'].append(np.mean(distances))

        # Set plot preferences.
        year_title_options = {
            'y': 0.8,
            'verticalalignment': 'top',
            'alpha': 0.6,
            'fontsize': 10,
        }
        
        fig = plt.figure(dpi=96,figsize=(9,6))
        gs = GridSpec(12, 2, width_ratios=[1,3])

        year_axs = {}
        for index, year in enumerate(range(self.start_year, self.end_year+1)):
            data = self.by_year_data[year]
            year_axs[index] = fig.add_subplot(gs[index, 0])
            year_axs[index].plot(data['dates'], data['distances'])
            is_bottom = (index == (self.end_year - self.start_year))
            self.apply_styles(year_axs[index], data, year, include_xaxis=is_bottom)
            for i, spine in year_axs[index].spines.items():
                spine.set_visible(False)
            year_axs[index].get_yaxis().set_visible(False)
            
            year_axs[index].set_xlim([date(year,1,1),date(year,12,31)])
            year_axs[index].set_ylim([-1000,12000])
            year_axs[index].set_yticks([0,6000,12000])
            year_axs[index].set_title(data['title'], **year_title_options)
            if is_bottom:
                month_letters = ["J","F","M","A","M","J","J","A","S","O","N","D"]
                year_axs[index].set_xticklabels(month_letters, minor=True)
            

        data = average_distance_data
        avg_ax = fig.add_subplot(gs[:, 1])
        avg_ax.plot(data['dates'], data['distances'])
        self.apply_styles(avg_ax, data, avg_year, include_xaxis=True)
        avg_ax.set_title(data['title'])

        y_max_miles = 3000
        y_max_km = y_max_miles * KM_PER_MILE

        avg_ax.set_ylim([0,y_max_miles])
        avg_ax.set_ylabel("Distance (miles)")

        avg_ax_km = avg_ax.twinx()
        avg_ax_km.set_ylim([0,y_max_km])
        avg_ax_km.set_ylabel("Distance (km)")

        fig.tight_layout()
        if self.output is None:
            plt.show()
        else:
            plt.savefig(self.output)
            print(f"Saved distance by day chart to {self.output}.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest='type')

    parser_single = subparsers.add_parser(
        'single',
        help="Create a chart for a single year.",
    )
    parser_single.add_argument(
        'year',
        type=int,
        help="Year to generate chart for"
    )
    
    parser_multi = subparsers.add_parser(
        'multi',
        help=(
            "Create charts for a range of years and a chart of all years "
            "averaged."
        )
    )
    parser_multi.add_argument(
        'start_year',
        type=int,
        help="Start year (inclusive)",
    )
    parser_multi.add_argument(
        'end_year',
        type=int,
        help="End year (inclusive)",
    )

    parser.add_argument(
        'output',
        type=Path,
        help="Output file(s) to save the graph to",
        default=None,
    )

    args = parser.parse_args()
    if args.type == 'single':
        main('single', [args.year], args.output)
    else:
        main('multi', [args.start_year, args.end_year], args.output)
    