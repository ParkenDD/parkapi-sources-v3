# Konstanz disabled

Konstanz provides a GeoJSON with Point geometry, which results in ParkingSpots. Some GeoJSON features have multiple
places without specific coordinates, the importer uses a distribution algorithm per default to not have them all on one
point.

* `purpose` is set to `CAR`
* `restricted_to.type` is set to `DISABLED`
* `has_realtime_data` is set to `false`
* `static_data_updated_at` is set to import datetime


## Properties

| Field      | Type    | Cardinality | Mapping       | Comment                                                                                                              |
|------------|---------|-------------|---------------|----------------------------------------------------------------------------------------------------------------------|
| OBJECTID   | integer | 1           | uid           |                                                                                                                      |
| Name       | string  | 1           | name, address | For `address`, everything after `/` or `,` will be cut off, and `, Konstanz` will be added in the end.               |
| Informatio | string  | 1           |               | Either `1 Behindertenparkplatz` or `{n} Behindertenparkplätze`. Will generate `n` `ParkingSpot`s in the latter case. |
| Themen     | string  | 1           |               |                                                                                                                      |
| GlobalID   | string  | 1           |               |                                                                                                                      |
