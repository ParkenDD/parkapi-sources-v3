# Friedrichshafen EasyPark

Friedrichshafen provides a CSV file from EasyPark. Therefore, this will be a push converter.

Static values:

* `name` is always have prefix of `Straßenparkplatz`
* `type` is always `PARKING_CENTER_LINE`
* `purpose` is always `CAR`
* `has_realtime_data` is always `false`
* Sites having the field `park_angle` with value `no_parking` should not be integrated.


| Field                  | Type                 | Cardinality | Mapping                                                         | Comment                                                                       |
|------------------------|----------------------|-------------|-----------------------------------------------------------------|-------------------------------------------------------------------------------|
| length                 | integer              | 1           | uid/capacity/[LinearParkingSiteSides](#LinearParkingSiteSides)  |                                                                               |
| park_angle             | string               | 1           | uid/[LinearParkingSiteSides](#LinearParkingSiteSides)           | Entries with `no_parking` should not be integrated.                           |
| street_side            | string               | 1           | uid/[LinearParkingSiteSides](#LinearParkingSiteSides)           |                                                                               |
| location_on_sidewalk   | numeric              | 1           | lat/lon/geojson                                                 | The center of the LineString coordinates is used as latitude and longitude    |
| Layer 1                | string               | 1           | name                                                            | To be used as suffix to the `name` prefix stated above.                       |
| permissions            | string               | 1           | description/fee_description                                     | To be used as fallback, If `permission_period` is not available               |
| permission_period      | string               | ?           | fee_description                                                 |                                                                               |
| time_limited           | string               | ?           | fee_description                                                 | If available, add to  `fee_description`                                       |


### ParkAngle

| Key           | Mapping       |
|---------------|---------------|
| parallel      | PARALLEL      |
| perpendicular | PERPENDICULAR |
| diagonal      | DIAGONAL      |
| no_parking    |               |


### ParkAngleCapacity

| Key           | Mapping       | Comment                                              |
|---------------|---------------|------------------------------------------------------|
| parallel      | capacity      | Calculate `capacity` with `Math.round(length / 5)`   |
| perpendicular | capacity      | Calculate `capacity` with `Math.round(length / 2.5)` |
| diagonal      | capacity      | Calculate `capacity` with `Math.round(length / 3)`   |
| no_parking    |               |                                                      |


### StreetSide

| Key       | Mapping |
|-----------|---------|
| right     | RIGHT   |
| left      | LEFT    |


### LinearParkingSiteSides

| Field               | Type        | Cardinality | Mapping                    | Comment                                                                       |
|---------------------|-------------|-------------|----------------------------|-------------------------------------------------------------------------------|
| length_cm/capacity  | integer     | 1           | length/                     |                                                                               |
| orientation         | string      | 1           | [ParkAngle](#ParkAngle)    | Entries with `no_parking` should not be integrated.                           |
| side                | string      | 1           | [StreetSide](#StreetSide)  |                                                                               |



