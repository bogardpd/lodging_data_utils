# Lodging Database Criteria for New vs. Updated Records

Stay location data is contained in the `stay_locations` layer of the [lodging GeoPackage](data_structure.md). Generally, there is a single record in this layer for each property that has hosted a stay.

In some situations, a new hotel or short-term rental may take over an existing property, or new owners may take over a residence, potentially resulting in multiple records for the same physical property. The following criteria identify when it’s appropriate to create another record for the same property, versus simply updating an existing record (with, for example, an updated name).

## Criteria

In general, new records should be created only when the guest experience substantially changes.

### Create a New Record For:

1. **Type Changes:** A location makes any change between being a hotel, a short-term rental, or a residence
2. **Brand Changes:** A hotel switches between existing brands or changes from independent to chain-affiliated (or vice versa), excluding brand splits and soft brand changes that don’t significantly change the hotel experience.
3. **Major Category Shifts:** A property changes significantly in class/quality (e.g., from budget to luxury)
4. **Complete Renovations:** A hotel underwent a comprehensive renovation with extended closure (3+ months) and substantially different experience
5. **Significant Layout/Room Changes:** Major alterations to room count, room types, or property footprint
6. **Different Location Experiences:** Even in the same building, if the entrance, lobby, or overall guest flow is completely reconfigured

### Update Existing Record For:

1. **Simple Name Changes:** Same property with a new marketing name, or with updated location information within the name
2. **Brand Splits:** A portfolio creates a new brand and moves the hotel to it without significantly changing the hotel experience
3. **Soft Brand Changes:** A named hotel changes soft brands without significantly changing the hotel experience
4. **Portfolio Changes:** A brand is moved to a new portfolio (i.e. a new loyalty program), but the brand itself doesn’t change
5. **Cosmetic Renovations:** Updates to decor, furnishings, or amenities without changing the fundamental experience
6. **Management Changes:** New operators but similar guest experience
