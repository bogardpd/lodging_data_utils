from modules.collections import DateCollection
from modules.hotel_data_frame import HotelDataFrame
from datetime import date

import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import matplotlib.ticker as ticker
from matplotlib.gridspec import GridSpec
import numpy as np

def apply_common_styles(ax, ax_data, year, include_xaxis=False):
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

HOME_LOCATION = "US/OH/Beavercreek"
START_YEAR = 2009
END_YEAR = 2020

hotel_df = HotelDataFrame()
locations = DateCollection(hotel_df, date(START_YEAR,1,1), date(END_YEAR,12,31),
    HOME_LOCATION)

# Create dictionary for each year of data.
by_year_data = {}
days_of_year = {}
for this_date, distance in locations.distances().items():
    # Store distance for each day in its year's dictionary.    
    if this_date.year not in by_year_data:
        by_year_data[this_date.year] = {
            'title': str(this_date.year),
            'dates': [],
            'distances': [],
        }
    by_year_data[this_date.year]['dates'].append(this_date)
    by_year_data[this_date.year]['distances'].append(distance)

    # Store distance in day of year for calculating averages.
    if this_date.month not in days_of_year:
        days_of_year[this_date.month] = {}
    if this_date.day not in days_of_year[this_date.month]:
        days_of_year[this_date.month][this_date.day] = []
    days_of_year[this_date.month][this_date.day].append(distance)

# Create a placeholder year to use for storing days of the year when
# calculating averages for each day. Should be a leap year so all days
# are included. 
avg_year = 2020

# Calculate averages.
average_distance_data = {
    'title': (f"Average Distance From Home by Day of Year "
        f"({START_YEAR}–{END_YEAR})"),
    'dates': [],
    'distances': [],
}
for month, days in days_of_year.items():
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

# Draw plots.

fig = plt.figure(dpi=96,figsize=(9,6))
gs = GridSpec(12, 2, width_ratios=[1,3])

year_axs = {}
for index, year in enumerate(range(START_YEAR, END_YEAR+1)):
    data = by_year_data[year]
    year_axs[index] = fig.add_subplot(gs[index, 0])
    year_axs[index].plot(data['dates'], data['distances'])
    is_bottom = (index == (END_YEAR - START_YEAR))
    apply_common_styles(year_axs[index], data, year, include_xaxis=is_bottom)
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
apply_common_styles(avg_ax, data, avg_year, include_xaxis=True)
avg_ax.set_title(data['title'])

y_max_miles = 3000
y_max_km = y_max_miles * 1.609

avg_ax.set_ylim([0,y_max_miles])
avg_ax.set_ylabel("Distance (miles)")

avg_ax_km = avg_ax.twinx()
avg_ax_km.set_ylim([0,y_max_km])
avg_ax_km.set_ylabel("Distance (km)")

fig.tight_layout()
plt.show()