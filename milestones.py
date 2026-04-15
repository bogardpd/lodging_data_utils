"""Shows dates for stay milestones."""
from lodging_data_utils import LodgingLog

MILESTONES = [50, 100, 200, 500, 1000, 2000, 5000, 10000, 20000, 50000]
TRANSIT = ['Flight']

def milestones():
    log = LodgingLog()
    mornings = log.mornings()
    mornings = mornings[~mornings['type'].isin(TRANSIT)]
    print(f"Excludes: {TRANSIT}")
    locations = log.geodata_cache['stay_locations']
    mornings = mornings.join(
        locations,
        on='stay_location_fid',
        rsuffix='_loc'
    )

    # Nights
    nights = mornings.copy()
    total_nights = len(nights)
    nights['night_number'] = range(1, len(nights) + 1)
    nights = nights[nights['night_number'].isin(MILESTONES)]
    print("\nNIGHTS AWAY FROM HOME")
    print(nights[['type', 'stay_location_fid', 'name', 'night_number']])
    print(f"Total nights away from home: {total_nights}")

    # Unique uniq_props
    uniq_props = mornings.copy()
    uniq_props = uniq_props.drop_duplicates(subset='stay_location_fid')
    total_props = len(uniq_props)
    uniq_props['property_number'] = range(1, len(uniq_props) + 1)
    uniq_props = uniq_props[uniq_props['property_number'].isin(MILESTONES)]
    print("\nUNIQUE LODGING PROPERTIES")
    print(uniq_props[['type', 'stay_location_fid', 'name', 'property_number']])
    print(f"Total unique lodging properties: {total_props}")

if __name__ == "__main__":
    milestones()