# Friedrichshafen EasyPark
Friedrichshafen provides a static CSV file of Onstreet Parking sites inventory. Therefore, this will be a push converter.

Static values:

* `name` is always `Straßenparkplatz`
* `type` is always `PARKING_CENTER_LINE` which is a `LinearParkingSiteType`
* `purpose` is always `CAR`
* `has_realtime_data` is always `false`
* Sites having the field `park_angle` with value `no_parking` should not be integrated.
* `has_fee` is always `true` if `permission_period` contains `Gebührenpflichtig`.


| Field                     | Type                        | Cardinality | Mapping                                                     | Comment                                                                                                                            |
|---------------------------|-----------------------------|-------------|-------------------------------------------------------------|------------------------------------------------------------------------------------------------------------------------------------|
| id                        | integer                     | 1           | uid                                                         |                                                                                                                                    |
| length                    | integer                     | 1           | [sides](#LinearParkingSiteSide)                             |                                                                                                                                    |
| street_side               | [StreetSide](#StreetSide)   | 1           | [sides](#LinearParkingSiteSide)                             |                                                                                                                                    |
| park_angle                | [ParkAngle](#ParkAngle)     | 1           | capacity/[sides](#LinearParkingSiteSide)                    | Use [ParkAngleCapacity](#ParkAngleCapacity) for the calculation of `capacity`. |
| location_on_sidewalk      | numeric                     | 1           | lat/lon/geojson                                             | The center of the LineString coordinates is used as latitude and longitude                                                         |
| permissions_translation   | string                      | 1           | description/fee_description                                 |                                                                                                                                    |
| permission_period         | string                      | ?           | fee_description                                             |                                                                                                                                    |
| time_limited              | string                      | ?           | fee_description                                             | If available, add to  `fee_description`                                                                                            |


### LinearParkingSiteSide

| Field           | Type                         | Cardinality | Mapping               | Comment                                                                          |
|-----------------|------------------------------|-------------|-----------------------|----------------------------------------------------------------------------------|
| length          | integer                      | 1           | length_cm             | `length` is in metres. Therefore, `length_cm = length * 100`                     |
| park_angle      | [ParkAngle](#ParkAngle)      | 1           | orientation/capacity  | Use [ParkAngleCapacity](#ParkAngleCapacity) for the calculation of `capacity`.   |
| street_side     | [StreetSide](#StreetSide)    | 1           | side                  |                                                                                  |


### ParkAngle

| Key           | Mapping       |
|---------------|---------------|
| parallel      | PARALLEL      |
| perpendicular | PERPENDICULAR |
| diagonal      | DIAGONAL      |
| no_parking    |               |


### ParkAngleCapacity

Since the capacity information is not provided, the field `length` (in metres) is used to calculate `capacity`.
The result of the capacity should be rounded down to whole numbers e.g. if `length/5 = 1.9` then `capacity: 1` 

| Key           | Mapping       | Comment                                                                                                                                          |
|---------------|---------------|--------------------------------------------------------------------------------------------------------------------------------------------------|
| parallel      | capacity      | Calculate `capacity` with `length / 5`, where 5 (in metres) is estimated vehicle length when parked parallel to the street side                  |
| perpendicular | capacity      | Calculate `capacity` with field `length / 2.5` , where 2.5 (in metres) is estimated vehicle length when parked perpendicular to the street side  |
| diagonal      | capacity      | Calculate `capacity` with field `length / 3` , where 3 (in metres) is estimated vehicle length when parked diagonally on the street side         |   


### StreetSide

| Key       | Mapping |
|-----------|---------|
| right     | RIGHT   |
| left      | LEFT    |







