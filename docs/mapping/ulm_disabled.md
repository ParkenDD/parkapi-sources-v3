# Ulm Disabled

Ulm provides a simple GeoJSON with Point geometry for disabled parking spots.

* `has_realtime_data` is set to `false`
* `static_data_updated_at` is set to the moment of import
* `purpose` is set to `CAR`
* `restricted_to.type` is set to `DISABLED`
* `uid` is set to `{lat}_{lon}`
* `lat` and `lon` are cut off 7 digits after the comma


| Field    | Type         | Cardinality | Mapping   | Comment                                                                               |
|----------|--------------|-------------|-----------|---------------------------------------------------------------------------------------|
| image    | string (url) | 1           | photo_url |                                                                                       |
| capacity | integer      | 1           |           | If capacity is more then 1, multiple slightly distributed `ParkingSpot`s are created. |
