# Bosch Service Solutions: Autohof Thiersheim

Bosch Service Solutions publishes the truck parking site of the Autohof Thiersheim as Datex II `ParkingTablePublication`
via the [Mobilithek](https://mobilithek.info/offers/608434098878160896). A parking site is represented by a
`parkingRecord` of type `InterUrbanParkingSite`. For each `parkingRecord` a `ParkingSite` is generated using the generic
class `InterUrbanParkingSiteMixin`. Realtime data is provided in a separate Datex II `ParkingStatusPublication` and
handled by the generic class `ParkingRecordStatusMixin`.

**Broken:** the static data is not valid DATEX II. The parking location has the coordinates `0` / `0`, so the parking
site fails the validation and no parking site is imported. The realtime data is imported, but references a parking site
which does not exist. Additionally, `contactDetailsStreet` and `contactDetailsHouseNumber` are swapped.

Static values:

* `purpose` is always `CAR`
* `type` is always `OFF_STREET_PARKING_GROUND` (derived from `interUrbanParkingSiteLocation`, which is always
  `motorway`)
* `has_realtime_data` is always `true`
* `capacity` is the sum of all `groupOfParkingSpaces`, as `parkingNumberOfSpaces` is not set
* `restrictions[0].type` is always `TRUCK`

| Datex II field                | Type                                                            | Cardinality | Mapping                | Comment                                    |
|-------------------------------|-----------------------------------------------------------------|-------------|------------------------|--------------------------------------------|
| @type                         | enum                                                            | 1           |                        | `xsi:type`, always `InterUrbanParkingSite` |
| @id                           | string                                                          | 1           | uid                    |                                            |
| @version                      | string                                                          | 1           |                        | always `1`                                 |
| parkingName.values.value      | string                                                          | 1           | name                   | German value (`lang="de"`)                 |
| parkingRecordVersionTime      | datetime                                                        | 1           | static_data_updated_at |                                            |
| operator                      | [operator](#operator)                                           | 1           | operator_name          |                                            |
| parkingLocation               | [parkingLocation](#parkingLocation)                             | 1           |                        | always `0` / `0`                           |
| tariffsAndPayment.chargeBand  | object                                                          | 1           |                        | one charge in `eur`, not used              |
| groupOfParkingSpaces          | [groupOfParkingSpaces](#groupOfParkingSpaces)                   | 1           | capacity, restrictions |                                            |
| parkingSiteAddress            | [parkingSiteAddress](#parkingSiteAddress)                       | 1           | address                |                                            |
| parkingAccess                 | [parkingAccess](#parkingAccess)                                 | 1           |                        |                                            |
| parkingStandardsAndSecurity   | object                                                          | 1           |                        | `parkingSecurity` always `unknown`         |
| interUrbanParkingSiteLocation | [InterUrbanParkingSiteLocation](#InterUrbanParkingSiteLocation) | 1           | type                   | always `motorway`                          |

### operator

| Datex II field                 | Type   | Cardinality | Mapping       | Comment                             |
|--------------------------------|--------|-------------|---------------|-------------------------------------|
| @type                          | enum   | 1           |               | `xsi:type`, always `ContactDetails` |
| contactOrganisationName.values | string | 1           | operator_name |                                     |

### parkingLocation

| Datex II field             | Type    | Cardinality | Mapping | Comment                    |
|----------------------------|---------|-------------|---------|----------------------------|
| @type                      | enum    | 1           |         | `xsi:type`, always `Point` |
| pointCoordinates.latitude  | numeric | 1           | lat     | always `0`                 |
| pointCoordinates.longitude | numeric | 1           | lon     | always `0`                 |

### groupOfParkingSpaces

| Datex II field                                                                   | Type    | Cardinality | Mapping                            | Comment                           |
|----------------------------------------------------------------------------------|---------|-------------|------------------------------------|-----------------------------------|
| parkingSpaceBasics.@type                                                         | enum    | 1           |                                    | always `GroupOfParkingSpaces`     |
| parkingSpaceBasics.parkingSpaceOrGroupIdentifier.values                          | string  | 1           |                                    | always `LKW-Plätze`               |
| parkingSpaceBasics.assignedParkingAmongOthers.vehicleCharacteristics.vehicleType | enum    | 1           | restrictions[0].type               | always `lorry`, mapped to `TRUCK` |
| parkingSpaceBasics.parkingNumberOfSpaces                                         | integer | 1           | capacity, restrictions[0].capacity | `55` in the test data             |
| parkingSpaceBasics.parkingTypeOfGroup                                            | enum    | 1           |                                    | always `other`                    |

### parkingSiteAddress

Assembled into `address` as `<street> <house number>, <postcode> <city>`. Components containing `n/a` are treated as
missing. As street and house number are swapped in the data, the address starts with the house number.

| Datex II field            | Type   | Cardinality | Mapping | Comment                   |
|---------------------------|--------|-------------|---------|---------------------------|
| @type                     | enum   | 1           |         | always `ContactDetails`   |
| contactDetailsStreet      | string | 1           | address | contains the house number |
| contactDetailsHouseNumber | string | 1           | address | contains the street       |
| contactDetailsPostcode    | string | 1           | address |                           |
| contactDetailsCity.values | string | 1           | address |                           |

### parkingAccess

| Datex II field                               | Type   | Cardinality | Mapping | Comment                                                        |
|----------------------------------------------|--------|-------------|---------|----------------------------------------------------------------|
| @id                                          | string | 1           |         |                                                                |
| accessCategory                               | enum   | 1           |         | always `vehicleEntrance`                                       |
| primaryRoad.roadIdentifier.values            | string | 1           |         | `A93`                                                          |
| primaryRoad.roadDestination.values           | string | 1           |         |                                                                |
| location.pointByCoordinates.pointCoordinates | object | 1           |         | coordinates without decimal point (degrees × 100000), not used |


## Realtime data

Each `parkingRecordStatus` references a `parkingRecord` by id.

| Datex II field                               | Type                                                  | Cardinality | Mapping                  | Comment                                       |
|----------------------------------------------|-------------------------------------------------------|-------------|--------------------------|-----------------------------------------------|
| @type                                        | enum                                                  | 1           |                          | `xsi:type`, always `ParkingSiteStatus`        |
| parkingRecordReference.@id                   | string                                                | 1           | uid                      | matched against the static `parkingRecord` id |
| parkingStatusOriginTime                      | datetime                                              | ?           | realtime_data_updated_at | defaults to import time if absent             |
| parkingOccupancy.parkingNumberOfVacantSpaces | integer                                               | 1           | realtime_free_capacity   | always `0`                                    |
| parkingSiteStatus                            | enum                                                  | 1           |                          | always `unknown`, not used                    |
| parkingSiteOpeningStatus                     | [ParkingSiteOpeningStatus](#ParkingSiteOpeningStatus) | 1           | realtime_opening_status  | always `statusUnknown`                        |


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
