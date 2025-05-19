# Reutlingen Disabled

Reutlingen provides a simple CSV which is transformed in `ParkingSpot`s.

* `has_realtime_data` is set to `false`
* `static_data_updated_at` is set to the moment of import
* `purpose` is set to `CAR`
* `restricted_to.type` is set to `DISABLED`

| Field | Type    | Cardinality | Mapping       | Comment                                 |
|-------|---------|-------------|---------------|-----------------------------------------|
| id    | integer | 1           | uid           |                                         |
| ort   | string  | 1           | name, address | Address gets a `, Reutlingen` attached. |
| GEOM  | integer | 1           | lat, lon      | Format is `POINT ({lon} {lat})`         |
