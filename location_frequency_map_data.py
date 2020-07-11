from datetime import date
from pathlib import Path
from modules.collections import DateCollection
from modules.hotel_data_frame import HotelDataFrame

OUTPUT_FILE_PATH = (Path.home()
        / Path("OneDrive/Projects/Maps/Hotel Nights/Data")
        / Path("Location Frequencies.csv"))

hotel_df = HotelDataFrame()
loc_freqs = hotel_df.location_frequencies()

with open(OUTPUT_FILE_PATH, 'w') as f:
    f.write("City,Latitude,Longitude,Frequency")
    for city, details in sorted(loc_freqs.items()):
        f.write(
            f"\n{city},"
            f"{details['latitude']},"
            f"{details['longitude']},"
            f"{details['frequency']}"
        )
    print(f"Wrote to {OUTPUT_FILE_PATH}")