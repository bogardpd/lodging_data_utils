from datetime import date
from pathlib import Path
from modules.collections import DateCollection
from modules.hotel_data_frame import HotelDataFrame

OUTPUT_DIR = Path.home() / Path("OneDrive/Projects/Maps/Hotel Nights/Data")

def main():
    hotel_df = HotelDataFrame()

    # Create CSV for all data.
    loc_freqs = hotel_df.location_frequencies()
    write_csv("All Dates.csv", loc_freqs)

    # Create CSV for each year.
    earliest_year = hotel_df.min_date().year
    latest_year = date.today().year
    for year in range(earliest_year, latest_year+1):
        year_loc_freqs = hotel_df.location_frequencies(
            start_date=date(year, 1, 1),
            end_date=date(year, 12, 31)
        )
        write_csv(f"{year}.csv", year_loc_freqs)

def write_csv(filename, data):
    filepath = OUTPUT_DIR / Path(filename)
    with open(filepath, 'w', encoding='UTF-8', newline='') as f:
        f.write("City,Latitude,Longitude,Frequency")
        for city, details in sorted(data.items()):
            f.write(
                f"\n{city},"
                f"{details['latitude']},"
                f"{details['longitude']},"
                f"{details['frequency']}"
            )
        print(f"Wrote to {filepath}")

if __name__ == "__main__":
    main()