# Heidelberg Disabled

Heidelberg provides a GeoJSON with Point geometry, which will create `ParkingSpot`s.

* `has_realtime_data` is set to `false`
* `static_data_updated_at` is set to the moment of import
* `purpose` is set to `CAR`
* `restricted_to.type` is set to `DISABLED`
* `uid` is set to `feature.id`


| Field      | Type          | Cardinality | Mapping       | Comment                                                                                  |
|------------|---------------|-------------|---------------|------------------------------------------------------------------------------------------|
| BEZEICHNUN | string        | 1           | name, address | For `address`, any content in brackets is removed. At `address`, ", Heidelberg"is added. |
| BETREIBER  | string        | ?           | operator_name |                                                                                          |
| TYP        | string        | ?           |               | Always 'öffentlich' or null                                                              |
| XTRID      | string or int | 1           |               |                                                                                          |
| URN        | string        | 1           |               |                                                                                          |
| BESCHREIBU | string        | ?           | description   |                                                                                          |
| BESCHRIFTU | string        | ?           | description   |                                                                                          |
| PARKPLATZ_ | string        | ?           |               | Always 'Behinderte'                                                                      |
| Notiz      | string        | ?           | description   | If it contains `Baustelle` dataset is ignored.                                           |
