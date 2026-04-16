# Friedrichshafen EasyPark

Friedrichshafen provides a static CSV file of Onstreet Parking sites inventory. Therefore, this will be a push converter.

Static values:

* `name` is always `Straßenparkplatz`
* `type` is always `PARKING_CENTER_LINE` which is a `LinearParkingSiteType`
* `purpose` is always `CAR`
* `has_realtime_data` is always `false`
* Sites having the field `park_angle` with value `no_parking` should not be integrated.
* `has_fee` is always `true` if `permission_period` contains `Gebührenpflichtig`.


| Field                     | Type                        | Cardinality | Mapping                                                     | Comment                                                                       |
|---------------------------|-----------------------------|-------------|-------------------------------------------------------------|-------------------------------------------------------------------------------|
| id                        | integer                     | 1           | uid                                                         |                                                                               |
| length                    | integer                     | 1           | capacity/[LinearParkingSiteSides](#LinearParkingSiteSides)  |                                                                               |
| park_angle                | [ParkAngle](#ParkAngle)     | 1           | [LinearParkingSiteSides](#LinearParkingSiteSides)           | Entries with `no_parking` should not be integrated.                           |
| street_side               | [StreetSide](#StreetSide)   | 1           | [LinearParkingSiteSides](#LinearParkingSiteSides)           |                                                                               |
| location_on_sidewalk      | numeric                     | 1           | lat/lon/geojson                                             | The center of the LineString coordinates is used as latitude and longitude    |
| permissions_translation   | string                      | 1           | description/fee_description                                 |                                                                               |
| permission_period         | string                      | ?           | fee_description                                             |                                                                               |
| time_limited              | string                      | ?           | fee_description                                             | If available, add to  `fee_description`                                       |


### ParkAngle

| Key           | Mapping       |
|---------------|---------------|
| parallel      | PARALLEL      |
| perpendicular | PERPENDICULAR |
| diagonal      | DIAGONAL      |
| no_parking    |               |


### ParkAngleCapacity

| Key           | Mapping       | Comment                                                  |
|---------------|---------------|----------------------------------------------------------|
| parallel      | capacity      | Calculate `capacity` with `length / 5` in whole number   |
| perpendicular | capacity      | Calculate `capacity` with `length / 2.5` in whole number |
| diagonal      | capacity      | Calculate `capacity` with `length / 3` in whole number   |
| no_parking    |               |                                                          |


### StreetSide

| Key       | Mapping |
|-----------|---------|
| right     | RIGHT   |
| left      | LEFT    |



### LinearParkingSiteSides

| Field           | Type                                        | Cardinality | Mapping               | Comment                                               |
|-----------------|---------------------------------------------|-------------|-----------------------|-------------------------------------------------------|
| park_angle      | [ParkAngleCapacity](#ParkAngleCapacity)     | 1           | length_cm/capacity    |                                                       |
| park_angle      | [ParkAngle](#ParkAngle)                     | 1           | orientation           | Entries with `no_parking` should not be integrated.   |
| street_side     | [StreetSide](#StreetSide)                   | 1           | side                  |                                                       |



