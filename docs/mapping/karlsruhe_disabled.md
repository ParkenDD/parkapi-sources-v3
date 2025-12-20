# Karlsruhe Disabled

Karlsruhe provides a GeoJSON with Point geometry for disabled parking spots.

* `purpose` is set to `CAR`
* `restricted_to.type` is set to `DISABLED`

## Static data

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
| sensorenliste | string             | ?           | has_realtime_data      | Comma separated list. If not null, `has_realtime_data` is set to `true`                         |


## Realtime data

| Field         | Type                      | Cardinality | Mapping | Comment                                |
|---------------|---------------------------|-------------|---------|----------------------------------------|
| id            | string                    | 1           |         | Will be used to match `sensorenliste`  |
| last_readings | list([Reading](#Reading)] | 1           |         |                                        |


### Reading

| Field | Type                         | Cardinality | Mapping | Comment |
|-------|------------------------------|-------------|---------|---------|
| data  | [ReadingData](#ReadingData)  | 1           |         |         |


### ReadingData

| Field          | Type                            | Cardinality | Mapping                  | Comment |
|----------------|---------------------------------|-------------|--------------------------|---------|
| parking_status | [ParkingStatus](#ParkingStatus) | 1           | status                   |         |
| measured_at    | string (date-time)              | 1           | realtime_data_updated_at |         |


### ParkingStatus

| Field | Mapping   |
|-------|-----------|
| 0     | AVAILABLE |
| 1     | TAKEN     |
