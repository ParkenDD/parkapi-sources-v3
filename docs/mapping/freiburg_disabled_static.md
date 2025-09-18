# Freiburg static disabled parking spots

Freiburg provides a GeoJSON with static parking spots. lat / lon are set to the center of the GeoJSON polygon.


* `restricted_to.type` is set to `DISABLED`
* `purpose` is set to `CAR`
* `has_realtime_data` is set to `false`
* `static_data_updated_at` is set to the moment of import

## Properties

| Field      | Type   | Cardinality | Mapping     | Comment                                                                |
|------------|--------|-------------|-------------|------------------------------------------------------------------------|
| fid        | string | 1           | uid         |                                                                        |
| strasse    | string | 1           | address     | Address without locality, therefore ', Freiburg im Breisgau' is added. |
| hausnummer | string | 1           | address     | Will be omitted if emptystring.                                        |
| anzahl     | string | 1           |             |                                                                        |
| hinweis    | string | 1           | description |                                                                        |
| stadtteil  | string | 1           |             |                                                                        |
