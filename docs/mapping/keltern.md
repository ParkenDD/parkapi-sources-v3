# Keltern

Keltern provides an Excel table with some static parking site data.

Static values:

* `purpose` is always `CAR`
* `has_realtime_data` is always `false`

| Field                                          | Type                  | Cardinality | Mapping                                 | Comment                                                                                           |
|------------------------------------------------|-----------------------|-------------|-----------------------------------------|---------------------------------------------------------------------------------------------------|
| id                                             | string                | 1           | uid                                     | Suffix `@GemeindeKeltern` is removed                                                              |
| name                                           | string                | 1           | name                                    |                                                                                                   |
| dataType                                       | [DataType](#DataType) | 1           |                                         | Info is already included in `type`, so no mapping.                                                |
| locations_type                                 | string                | 1           |                                         | Always `Point`                                                                                    |
| locations_longitude                            | string                | 1           | lon                                     | `,` as decimal separator                                                                          |
| locations_latitude                             | string                | 1           | lat                                     | `,` as decimal separator                                                                          |
| operatorID                                     | string                | 1           | operator_name                           |                                                                                                   |
| networkID                                      | string                | 1           |                                         |                                                                                                   |
| timestamp                                      | string (date)         | 1           | static_data_updated_at                  |                                                                                                   |
| adress_str                                     | string                | 1           | address                                 |                                                                                                   |
| adress_hou                                     | string                | 1           |                                         | Always `-`                                                                                        |
| adress_pos                                     | string                | 1           | address                                 |                                                                                                   |
| adress_cit                                     | string                | 1           | address                                 |                                                                                                   |
| adress_dis                                     | string                | 1           |                                         |                                                                                                   |
| adress_sta                                     | string                | 1           |                                         |                                                                                                   |
| adress_cou                                     | string                | 1           |                                         |                                                                                                   |
| trafficTyp                                     | string                | 1           |                                         | Always `car`                                                                                      |
| descriptio                                     | string                | 1           | description                             | If content is `-`, the field is ignored                                                           |
| type                                           | [Type](#Type)         | 1           | type, park_and_ride_type, restricted_to |                                                                                                   |
| geometry_type                                  | string                | 1           |                                         | Always `Point`                                                                                    |
| geometry_longitude                             | string                | 1           |                                         | `,` as decimal separator                                                                          |
| geometry_latitude                              | string                | 1           |                                         | `,` as decimal separator                                                                          |
| quantitySpacesReservedForWomen                 | integer               | 1           | capacity_women                          |                                                                                                   |
| quantitySpacesReservedForMobilityImpededPerson | integer               | 1           | capacity_disabled                       |                                                                                                   |
| securityInformation                            | string                | 1           |                                         | Always `-`                                                                                        |
| feeInformation                                 | string                | 1           |                                         | Always `-`                                                                                        |
| properties                                     | [Property](#Property) | 1           |                                         | Format: `[value_1, value_2]`, `-` for no data. Info is already included in `type`, so no mapping. |
| capacity                                       | integer               | 1           | capacity                                |                                                                                                   |
| hasChargingStation                             | boolean               | 1           | capacity_charging                       | `true` for true, `false` for false. Mapped to 1 for true, because we don't have an actual number. |
| hasOpeningHours24h                             | boolean               | 1           | opening_hours                           | `true` for true, `false` for false, `24/7` if `true`, `null` if `false`                           |
| openingHours                                   | string                | 1           | description                             | `24h, 7 Tage` will not be mapped to description                                                   |
| source                                         | string                | 1           |                                         |                                                                                                   |
| tariffPrices_id                                | integer               | 1           |                                         | Always 0                                                                                          |
| tariffPrices_duration                          | integer               | 1           |                                         | Always 0                                                                                          |
| tariffPrices_price                             | integer               | 1           |                                         | Always 0                                                                                          |


### DataType

| Key          | Mapping   |
|--------------|-----------|
| parkingCar   | TAKEN     |
| parkingSpace | AVAILABLE |


### Type

| Key         | Mapping                                                            |
|-------------|--------------------------------------------------------------------|
| onStreet    | `type` = `ON_STREET`                                               |
| carPark     | `type` = `OFF_STREET_PARKING_GROUND`                               |
| parkAndRide | `type` = `OFF_STREET_PARKING_GROUND`, `park_and_ride_type` = `YES` |
| handicapped | `type` = `ON_STREET`, `restricted_to.type` = `DISABLED`            |


### Property

| Key         | Mapping                      |
|-------------|------------------------------|
| carpark     | `type` = `CAR_PARK`          |
| parkAndRide | `park_and_ride_type` = `YES` |
