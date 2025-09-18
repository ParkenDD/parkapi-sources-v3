# Heidelberg EasyPark

Heidelberg provides a large GeoJSON file which was created by EasyPark. Coordinates are in UTM32 and have to be
transformed to WSG84. All properties can be emptystring, which is converted to not set.

Static values:

* `purpose` is always `CAR`
* `has_realtime_data` is always `false`


| Field      | Type                        | Cardinality | Mapping                  | Comment                                                                                     |
|------------|-----------------------------|-------------|--------------------------|---------------------------------------------------------------------------------------------|
| Segment    | integer                     | 1           | uid                      | Segment is a street, so it's not unique, but together with the position = 'Abstand', it is. |
| Abstand1   | string (decimal)            | 1           | uid                      |                                                                                             |
| Abstand2   | string (decimal)            | 1           | uid                      |                                                                                             |
| Länge      | string (decimal)            | 1           |                          |                                                                                             |
| Parkwinkel | [Orientation](#Orientation) | 1           | name                     | Same as `Ausrichtun`                                                                        |
| Straßense  | [Straßense](#Straßense)     | 1           | name                     |                                                                                             |
| Bewirtscha | string                      | 1           | has_fee, fee_description | has_fee is set to True if not emptystring                                                   |
| Erlaubnis  | string                      | 1           | description              |                                                                                             |
| Erlaubnisz | string                      | 1           | description              |                                                                                             |
| Zeitlimit  | string                      | 1           | description              |                                                                                             |
| Zeitlimitz | string                      | 1           | description              |                                                                                             |
| Ausrichtun | [Orientation](#Orientation) | 1           | name                     | Value "Parkverbot" means that the dataset is ignored                                        |
| Kapazität  | string  (decimal)           | 1           | capacity                 |                                                                                             |
| Bildname   | string                      | 1           |                          |                                                                                             |
| Datenerfas | string (date-time)          | 1           |                          |                                                                                             |
| Straßenna  | string                      | 1           | address                  |                                                                                             |
| Stadtteile | string                      | 1           |                          |                                                                                             |
| Lage       | string                      | 1           |                          |                                                                                             |
| Position_a | string                      | 1           |                          | SQL compatible linestring. GeoJSON geometry is better source for us.                        |


### Orientation

| Key         | Mapping       |
|-------------|---------------|
| Parallel    | PARALLEL      |
| Senkrecht   | PERPENDICULAR |
| Diagonal    | DIAGONAL      |
| Parkverbot  |               |


### Straßense

| Key        | Mapping |
|------------|---------|
| rechts     | RIGHT   |
| links      | LEFT    |
