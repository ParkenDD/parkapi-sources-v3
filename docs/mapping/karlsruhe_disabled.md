# Karlsruhe Disabled

Karlsruhe provides a GeoJSON with Point geometry for disabled parking spots.

* `has_realtime_data` is set to `false`
* `purpose` is set to `CAR`
* `restricted_to.type` is set to `DISABLED`

| Field         | Type               | Cardinality | Mapping                | Comment                                                                                         |
|---------------|--------------------|-------------|------------------------|-------------------------------------------------------------------------------------------------|
| id            | integer            | 1           | uid                    |                                                                                                 |
| gemeinde      | string             | 1           | name, address          | `address` will be `{standort}, {gemeinde}`. `name` will be `{standort}, {gemeinde} {stadtteil}` |
| stadtteil     | string             | ?           |                        |                                                                                                 |
| standort      | string             | 1           | name, address          |                                                                                                 |
| parkzeit      | string             | ?           | description            | Unclear format, no reliable converter to `restricted_to.hours` possible.                        |
| max_parkdauer | string             | ?           | description            | Unclear format, no reliable converter to `restricted_to.may_stay` possible.                     |
| stellplaetze  | integer            | 1           |                        | If stellplaetze is more then 1, multiple slightly distributed `ParkingSpot`s are created.       |
| bemerkung     | string             | ?           | description            |                                                                                                 |
| stand         | string (date-time) | 1           | static_data_updated_at |                                                                                                 |
