# Konstanz disabled

Konstanz provides a GeoJSON with Point geometry, which results in ParkingSpots.

* `lat` and `lon` taken from geometry.coordinates, need to be rounded up to 7 digits
* `purpose` is set to `CAR`
* `restrictions.type` is set to `DISABLED`
* `has_realtime_data` is set to `false`
* `static_data_updated_at` is set to import datetime

## Properties

| field       | type            | Cardinality | Target field | Comment                          |
|-------------|-----------------|-------------|--------------|----------------------------------|
| OBJECTID    | integer         | 1           | uid          |                                  |
| Name        | string          | 1           | name         | name set to "`Name`-`Stadtteil`" |
| adress      | string          | 1           | address      |                                  |
| Stadteil    | string          | 1           | name         |Mapped to Name                    |
| type        | ParkingSpotType | 1           | type         |                                  |
| Anordnung   | string          | 1           |              |                                  |
| Breite      | string          | 1           |              |                                  |
| description | string          | ?           | description  | Set if present                   |
| GlobalID    | string          | 1           |              |                                  |


## ParkingSpotType
* ON_STREET
* OFF_STREET_PARKING_GROUND
