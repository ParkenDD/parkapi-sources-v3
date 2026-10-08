# Konstanz disabled

Konstanz provides a GeoJSON with Point geometry, which results in ParkingSpots.

* `lat` and `lon` taken from geometry.coordinates, need to be rounded up to 7 digits
* `purpose` is set to `CAR`
* `restrictions.type` is set to `DISABLED`
* `has_realtime_data` is set to `false`
* `static_data_updated_at` is set to import datetime

## Properties

| field        | type                                | Cardinality | Target field | Comment                          |
|--------------|-------------------------------------|-------------|--------------|----------------------------------|
| OBJECTID     | integer                             | 1           |              |                                  |
| Name         | string                              | 1           | name         | name set to "`Name`-`Stadtteil`" |
| Straßennummer| string                              | 1           |              |                                  |
| adress       | string                              | 1           | address      |                                  |
| Stadtteil    | string                              | 1           | name         | mapped to Name                   |
| type         | [ParkingSpotType](#ParkingSpotType) | 1           | type         |                                  |
| Anordnung    | [Anordnung](#Anordnung)             | 1           | orientation  |                                  |
| Breite       | string                              | 1           |              |                                  |
| description  | string                              | ?           | description  | set if present                   |
| GlobalID     | string                              | 1           | uid          |                                  |


### ParkingSpotType

| Key                      | Mapping: type             |
| ------------------------ | ------------------------- |
| OFF_STREET_PARKING_GROUND| OFF_STREET_PARKING_GROUND |
| ON_STREET                | ON_STREET                 |

### Anordnung

| Key         | Mapping       |
|-------------|---------------|
| längs       | PARALLEL      |
| quer        | PERPENDICULAR |
| schräg      | DIAGONAL      |
