# Bosch Service Solutions: Rastpark 24

Bosch Service Solutions publishes the truck parking site Rastpark 24 in Hengersberg as Datex II
`ParkingTablePublication` via the [Mobilithek](https://mobilithek.info/offers/925787550685814784). The publication
contains one `parkingRecord` of type `InterUrbanParkingSite`. For each `parkingRecord` a `ParkingSite` is generated
using the generic class `InterUrbanParkingSiteMixin`. Realtime data is provided in a separate Datex II
`ParkingStatusPublication` and handled by the generic class `ParkingRecordStatusMixin`.

Static values:

* `purpose` is always `CAR`
* `type` is always `OFF_STREET_PARKING_GROUND` (derived from `interUrbanParkingSiteLocation`, which is always
  `nearbyMotorway`)
* `has_realtime_data` is always `true`
* no `restrictions` are set, as there are no `groupOfParkingSpaces`
* parking records with a `parkingNumberOfSpaces` of `0` are ignored

| Datex II field                | Type                                                            | Cardinality | Mapping                | Comment                                    |
|-------------------------------|-----------------------------------------------------------------|-------------|------------------------|--------------------------------------------|
| @type                         | enum                                                            | 1           |                        | `xsi:type`, always `InterUrbanParkingSite` |
| @id                           | string                                                          | 1           | uid                    |                                            |
| @version                      | string                                                          | 1           |                        | timestamp                                  |
| parkingName.values.value      | string                                                          | 1           | name                   | German value (`lang="DE"`)                 |
| parkingRecordVersionTime      | datetime                                                        | 1           | static_data_updated_at |                                            |
| parkingNumberOfSpaces         | integer                                                         | 1           | capacity               | the parking site is ignored if `0`         |
| parkingOccupanyDetectionType  | enum                                                            | 1           |                        | always `balancing`                         |
| operator                      | [operator](#operator)                                           | 1           | operator_name          |                                            |
| parkingLocation               | [parkingLocation](#parkingLocation)                             | 1           |                        |                                            |
| onlyAssignedParking           | object                                                          | 1           |                        | without content, not used                  |
| parkingSiteAddress            | [parkingSiteAddress](#parkingSiteAddress)                       | 1           | address                |                                            |
| parkingAccess                 | [parkingAccess](#parkingAccess)                                 | 1           |                        |                                            |
| parkingStandardsAndSecurity   | [parkingStandardsAndSecurity](#parkingStandardsAndSecurity)     | 1           |                        |                                            |
| interUrbanParkingSiteLocation | [InterUrbanParkingSiteLocation](#InterUrbanParkingSiteLocation) | 1           | type                   | always `nearbyMotorway`                    |

### operator

| Datex II field                 | Type   | Cardinality | Mapping       | Comment                                                    |
|--------------------------------|--------|-------------|---------------|------------------------------------------------------------|
| @type                          | enum   | 1           |               | `xsi:type`, always `ContactDetails`                        |
| contactOrganisationName.values | string | 1           | operator_name | `K Gastronomie GmbH`; an empty value is treated as missing |

### parkingLocation

| Datex II field             | Type    | Cardinality | Mapping | Comment                    |
|----------------------------|---------|-------------|---------|----------------------------|
| @type                      | enum    | 1           |         | `xsi:type`, always `Point` |
| pointCoordinates.latitude  | numeric | 1           | lat     |                            |
| pointCoordinates.longitude | numeric | 1           | lon     |                            |

### parkingSiteAddress

Assembled into `address` as `<street> <house number>, <postcode> <city>`. Components containing `n/a` are treated as
missing.

| Datex II field            | Type   | Cardinality | Mapping | Comment                 |
|---------------------------|--------|-------------|---------|-------------------------|
| @type                     | enum   | 1           |         | always `ContactDetails` |
| contactDetailsStreet      | string | 1           | address |                         |
| contactDetailsHouseNumber | string | 1           | address |                         |
| contactDetailsPostcode    | string | 1           | address |                         |
| contactDetailsCity.values | string | 1           | address |                         |

### parkingAccess

| Datex II field                               | Type   | Cardinality | Mapping | Comment                             |
|----------------------------------------------|--------|-------------|---------|-------------------------------------|
| @id                                          | string | 1           |         |                                     |
| accessCategory                               | enum   | 1           |         | always `unspecified`                |
| primaryRoad.roadIdentifier.values            | string | 1           |         | street of the address               |
| primaryRoad.roadDestination.values           | string | 1           |         | city of the address                 |
| location.pointByCoordinates.pointCoordinates | object | 1           |         | same as `parkingLocation`, not used |

### parkingStandardsAndSecurity

| Datex II field     | Type | Cardinality | Mapping | Comment                                |
|--------------------|------|-------------|---------|----------------------------------------|
| parkingSecurity    | enum | 1           |         | always `areaSeperatedFromSurroundings` |
| parkingSupervision | enum | 1           |         | always `remote`                        |


## Realtime data

Each `parkingRecordStatus` references a `parkingRecord` by id.

| Datex II field                                 | Type                                                  | Cardinality | Mapping                  | Comment                                |
|------------------------------------------------|-------------------------------------------------------|-------------|--------------------------|----------------------------------------|
| @type                                          | enum                                                  | 1           |                          | `xsi:type`, always `ParkingSiteStatus` |
| parkingRecordReference.@id                     | string                                                | 1           | uid                      |                                        |
| parkingStatusOriginTime                        | datetime                                              | ?           | realtime_data_updated_at | defaults to import time if absent      |
| parkingOccupancy.parkingNumberOfVacantSpaces   | integer                                               | 1           | realtime_free_capacity   |                                        |
| parkingOccupancy.parkingNumberOfOccupiedSpaces | integer                                               | 1           |                          | not used, as vacant spaces are given   |
| parkingOccupancy.parkingOccupancy              | numeric                                               | 1           |                          | occupancy in percent, not used         |
| parkingSiteOpeningStatus                       | [ParkingSiteOpeningStatus](#ParkingSiteOpeningStatus) | ?           | realtime_opening_status  | not set in the test data               |


## Enumerations

### InterUrbanParkingSiteLocation

Mapped to `type`. Any other or missing value falls back to `OFF_STREET_PARKING_GROUND`.

| Key            | Mapping                   |
|----------------|---------------------------|
| motorway       | OFF_STREET_PARKING_GROUND |
| nearbyMotorway | OFF_STREET_PARKING_GROUND |
| layBy          | OFF_STREET_PARKING_GROUND |
| onStreet       | ON_STREET                 |
| other          | OFF_STREET_PARKING_GROUND |

### ParkingSiteOpeningStatus

Mapped to `realtime_opening_status`. Any other value leaves `realtime_opening_status` empty.

| Key            | Mapping |
|----------------|---------|
| open           | OPEN    |
| closed         | CLOSED  |
| closedAbnormal | CLOSED  |
| statusUnknown  | UNKNOWN |
