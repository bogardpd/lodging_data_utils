# Lodging Database Criteria for New vs. Updated Records

Lodging location data is contained in a Lodging.gpkg GeoPackage file, in a layer named `lodging_locations`. Generally, there is a single record in this layer for each property that has hosted a stay.

In some situations, a new hotel or short-term rental may take over an existing property, potentially resulting in multiple records for the same physical property. The following criteria identify when it’s appropriate to create another record for the same property, versus simply updating an existing record (with, for example, an updated name).

## Criteria

### Create a New Record For:

1. **Brand Change:** The hotel switches brands or changes from independent to chain-affiliated (or vice versa)
2. **Major Category Shift:** The property changes significantly in class/quality (e.g., from budget to luxury)
3. **Complete Renovation:** The hotel underwent a comprehensive renovation with extended closure (3+ months) and substantially different experience
4. **Significant Layout/Room Change:** Major alterations to room count, room types, or property footprint
5. **Different Location Experience:** Even in the same building, if the entrance, lobby, or overall guest flow is completely reconfigured

### Update Existing Record For:

1. **Name Change Only:** Same property with a new marketing name, or with updated location information within the name
2. **Portfolio Changes:** The brand is moved to a new portfolio (i.e. a new loyalty program), but the brand itself doesn’t change
3. **Cosmetic Renovations:** Updates to decor, furnishings, or amenities without changing the fundamental experience
4. **Management Changes:** New operators but similar guest experience

----

*Note: These criteria were initially developed with assistance from Claude 3.7 Sonnet (March 2025) and subsequently modified to meet the needs of this project.*