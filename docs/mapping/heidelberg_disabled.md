# Heidelberg Disabled

Heidelberg provides a GeoJSON with Point geometry, which will create `ParkingSpot`s.

* `has_realtime_data` is set to `false`
* `static_data_updated_at` is set to the moment of import
* `purpose` is always set to `CAR`

| Field      | Type   | Cardinality | Mapping       | Comment                     |
|------------|--------|-------------|---------------|-----------------------------|
| BEZEICHNUN | string | 1           | name          |                             |
| BETREIBER  | string | ?           | operator_name |                             |
| TYP        | string | ?           |               | Always 'öffentlich' or null |
| XTRID      | string | 1           | uid           |                             |
| URN        | string | 1           |               |                             |
| BESCHREIBU | string | ?           | description   |                             |
| BESCHRIFTU | string | ?           | description   |                             |
| PARKPLATZ_ | string | ?           |               | Always 'Behinderte'         |
| Notiz      | string | ?           |               |                             |
