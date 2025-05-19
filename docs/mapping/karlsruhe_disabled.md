# Ulm Disabled

Ulm provides a GeoJSON with Point geometry for disabled parking spots.

* `has_realtime_data` is set to `false`
* `purpose` is set to `CAR`
* `restricted_to.type` is set to `DISABLED`

| Field         | Type               | Cardinality | Mapping                | Comment                                                                                   |
|---------------|--------------------|-------------|------------------------|-------------------------------------------------------------------------------------------|
| id            | integer            | 1           | uid                    |                                                                                           |
| gemeinde      | string             | 1           | address                |                                                                                           |
| stadtteil     | string             | 1           | address                |                                                                                           |
| standort      | string             | 1           | name                   |                                                                                           |
| parkzeit      | integer            | ?           | description            |                                                                                           |
| max_parkdauer | string             | ?           | description            |                                                                                           |
| stellplaetze  | integer            | 1           |                        | If stellplaetze is more then 1, multiple slightly distributed `ParkingSpot`s are created. |
| bemerkung     | strong             | 1           | description            |                                                                                           |
| stand         | string (date-time) | 1           | static_data_updated_at |                                                                                           |
