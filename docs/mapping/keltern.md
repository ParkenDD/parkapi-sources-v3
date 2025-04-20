****# Keltern

Keltern provides an Excel table with some static parking site data.

Static values:

* `purpose` is always `CAR`

| Field                                          | Type                  | Cardinality | Mapping                                 | Comment                                                |
|------------------------------------------------|-----------------------|-------------|-----------------------------------------|--------------------------------------------------------|
| id                                             | string                | 1           | uid                                     |                                                        |
| name                                           | string                | 1           | name                                    |                                                        |
| dataType                                       | [Status](#Status)     | 1           |                                         |                                                        |
| locations_type                                 | string                | 1           |                                         | Always `Point`                                         |
| locations_longitude                            | string                | 1           | lon                                     | `,` as decimal separator                               |
| locations_latitude                             | string                | 1           | lat                                     | `,` as decimal separator                               |
| operatorID                                     | string                | 1           | operator_name                           |                                                        |
| networkID                                      | string                | 1           |                                         |                                                        |
| timestamp                                      | string (date)         | 1           | static_data_updated_at                  |                                                        |
| adress_str                                     | string                | 1           | address                                 |                                                        |
| adress_hou                                     | string                | 1           |                                         | Always `-`                                             |
| adress_pos                                     | string                | 1           | address                                 |                                                        |
| adress_cit                                     | string                | 1           | address                                 |                                                        |
| adress_dis                                     | string                | 1           |                                         |                                                        |
| adress_sta                                     | string                | 1           |                                         |                                                        |
| adress_cou                                     | string                | 1           |                                         |                                                        |
| trafficTyp                                     | string                | 1           |                                         | Always `car`                                           |
| descriptio                                     | string                | 1           | description                             |                                                        |
| type                                           | [Type](#Type)         | 1           | type, park_and_ride_type, restricted_to |                                                        |
| geometry_type                                  | string                | 1           |                                         | Always `Point`                                         |
| geometry_longitude                             | string                | 1           |                                         | `,` as decimal separator                               |
| geometry_latitude                              | string                | 1           |                                         | `,` as decimal separator                               |
| quantitySpacesReservedForWomen                 | integer               | 1           | capacity_women                          |                                                        |
| quantitySpacesReservedForMobilityImpededPerson | integer               | 1           | capacity_disabled                       |                                                        |
| securityInformation                            | string                | 1           |                                         | Always emptystring                                     |
| feeInformation                                 | string                | 1           |                                         | Always `-`                                             |
| properties                                     | [Property](#Property) | 1           | type, park_and_ride_type                | Format: `[value_1, value_2]`, `-` for no data          |
| capacity                                       | integer               | 1           | capacity                                |                                                        |
| hasChargingStation                             | boolean               | 1           |                                         | `true` for true, `false` for false                     |
| hasOpeningHours24h                             | boolean               | 1           | opening_hours                           | `true` for true, `false` for false, `24/7` when `true` |
| openingHours                                   | string                | 1           | description                             |                                                        |
| source                                         | string                | 1           |                                         |                                                        |
| tariffPrices_id                                | integer               | 1           |                                         | Always 0                                               |
| tariffPrices_duration                          | integer               | 1           |                                         | Always 0                                               |
| tariffPrices_price                             | integer               | 1           |                                         | Always 0                                               |


### DataType

| Key          | Mapping   |
|--------------|-----------|
| parkingCar   | TAKEN     |
| parkingSpace | AVAILABLE |


### Type

| Key         | Mapping                           |
|-------------|-----------------------------------|
| onStreet    | `type` = `ON_STREET`              |
| carPark     | `type` = `CAR_PARK`               |
| parkAndRide | `park_and_ride_type` = `YES`      |
| handicapped | `restricted_to.type` = `DISABLED` |


### Property

| Key         | Mapping                      |
|-------------|------------------------------|
| carpark     | `type` = `CAR_PARK`          |
| parkAndRide | `park_and_ride_type` = `YES` |
