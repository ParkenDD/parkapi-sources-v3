# ivm: P+R Hessen

ivm (Integriertes Verkehrs- und Mobilitätsmanagement Region Frankfurt RheinMain GmbH) publishes park and ride sites in
Hesse as Datex II v3 `ParkingTablePublication` via the [Mobilithek](https://mobilithek.info/offers/986574757105147904).
A parking site is represented by a `parkingRecord` of type `UrbanParkingSite`. For each `parkingRecord` a `ParkingSite`
is generated using the generic class `UrbanParkingSiteV3Mixin`. Realtime data is provided in a separate Datex II v3
`ParkingStatusPublication` and handled by the generic class `ParkingRecordStatusV3Mixin`.

**Broken:** the data is not valid DATEX II. The root element is `PayloadPublication` instead of `payload`, so the static
and the realtime import fail with one error each and no parking site is imported. The mapping below describes how the
fields would be mapped with a valid root element.

Static values:

* `purpose` is always `CAR`
* `has_realtime_data` is always `true`
* `park_and_ride_type` is always `[YES]`, as `parkingUsageScenario` is always `parkAndRide`

| Datex II field            | Type                                          | Cardinality | Mapping                | Comment                                                |
|---------------------------|-----------------------------------------------|-------------|------------------------|--------------------------------------------------------|
| @type                     | enum                                          | 1           |                        | `xsi:type`, always `UrbanParkingSite`                  |
| @id                       | string                                        | 1           | uid                    | UUID                                                   |
| @version                  | string                                        | 1           |                        | always `v1`                                            |
| parkingName.values        | string                                        | 1           | name                   | German value preferred, otherwise the first value      |
| parkingAlias.values       | string                                        | 1           |                        | e.g. `3002201PR01`                                     |
| parkingDescription.values | string                                        | ?           | description            |                                                        |
| parkingRecordVersionTime  | datetime                                      | 1           | static_data_updated_at |                                                        |
| parkingNumberOfSpaces     | integer                                       | ?           | capacity               | required, parking sites without it fail the validation |
| parkingLocation           | [parkingLocation](#parkingLocation)           | 1           |                        |                                                        |
| tariffsAndPayment         | [tariffsAndPayment](#tariffsAndPayment)       | 1           |                        |                                                        |
| groupOfParkingSpaces      | [groupOfParkingSpaces](#groupOfParkingSpaces) | *           | restrictions           |                                                        |
| parkingUsageScenario      | [parkingUsageScenario](#parkingUsageScenario) | 1           | park_and_ride_type     |                                                        |
| openingTimes              | [openingTimes](#openingTimes)                 | 1           |                        |                                                        |
| parkingAccess             | [parkingAccess](#parkingAccess)               | 1           |                        |                                                        |
| urbanParkingSiteType      | [UrbanParkingSiteType](#UrbanParkingSiteType) | 1           | type                   | `offStreetParking` or `other`                          |

### parkingLocation

| Datex II field                                                | Type    | Cardinality | Mapping | Comment                            |
|---------------------------------------------------------------|---------|-------------|---------|------------------------------------|
| @type                                                         | enum    | 1           |         | `xsi:type`, always `PointLocation` |
| coordinatesForDisplay                                         | object  | 1           |         | same as `pointByCoordinates`       |
| supplementaryPositionalDescription.locationDescription.values | string  | 1           |         | postcode and city                  |
| pointByCoordinates.pointCoordinates.latitude                  | numeric | 1           | lat     |                                    |
| pointByCoordinates.pointCoordinates.longitude                 | numeric | 1           | lon     |                                    |

### tariffsAndPayment

| Datex II field                      | Type    | Cardinality | Mapping | Comment                       |
|-------------------------------------|---------|-------------|---------|-------------------------------|
| paymentAdditionalDescription.values | string  | ?           |         | e.g. `Parkdauer: unbegrenzt`  |
| freeOfCharge                        | boolean | 1           | has_fee | `has_fee = not(freeOfCharge)` |

### groupOfParkingSpaces

Each group with `onlyAssignedParking` and a `parkingNumberOfSpaces` other than `0` is mapped to a restriction.

| Datex II field                                           | Type                  | Cardinality | Mapping                 | Comment                        |
|----------------------------------------------------------|-----------------------|-------------|-------------------------|--------------------------------|
| @groupIndex                                              | integer               | 1           |                         |                                |
| parkingSpaceBasics.@type                                 | enum                  | 1           |                         | always `GroupOfParkingSpaces`  |
| parkingSpaceBasics.parkingSpaceOrGroupIdentifier.values  | string                | 1           |                         | always `Behindertenparkplätze` |
| parkingSpaceBasics.onlyAssignedParking.applicableForUser | [UserType](#UserType) | 1           | restrictions[].type     | always `handicapped`           |
| parkingSpaceBasics.parkingNumberOfSpaces                 | integer               | 1           | restrictions[].capacity | groups with `0` are ignored    |
| parkingSpaceBasics.parkingTypeOfGroup                    | enum                  | 1           |                         | always `statisticsOnly`        |

### parkingUsageScenario

| Datex II field                                      | Type    | Cardinality | Mapping            | Comment                                                |
|-----------------------------------------------------|---------|-------------|--------------------|--------------------------------------------------------|
| @scenarioIndex                                      | integer | 1           |                    |                                                        |
| parkingUsageScenario.parkingUsageScenario           | enum    | 1           | park_and_ride_type | always `parkAndRide`, mapped to `[YES]`                |
| parkingUsageScenario._parkingUsageScenarioExtension | object  | 1           |                    | nearby public transport stop with name and description |

### openingTimes

| Datex II field   | Type    | Cardinality | Mapping       | Comment                    |
|------------------|---------|-------------|---------------|----------------------------|
| available24hours | boolean | 1           | opening_hours | `true` is mapped to `24/7` |

### parkingAccess

| Datex II field                | Type   | Cardinality | Mapping | Comment                         |
|-------------------------------|--------|-------------|---------|---------------------------------|
| @id                           | string | 1           |         |                                 |
| accessCategory                | enum   | 1           |         | always `vehicleEntranceAndExit` |
| primaryRoad.nameOfRoad.values | string | 1           |         |                                 |


## Realtime data

Each `parkingRecordStatus` references a `parkingRecord` by id.

| Datex II field                               | Type     | Cardinality | Mapping                  | Comment                                |
|----------------------------------------------|----------|-------------|--------------------------|----------------------------------------|
| @type                                        | enum     | 1           |                          | `xsi:type`, always `ParkingSiteStatus` |
| parkingRecordReference.@id                   | string   | 1           | uid                      |                                        |
| parkingStatusOriginTime                      | datetime | ?           | realtime_data_updated_at | defaults to import time if absent      |
| parkingOccupancy.parkingNumberOfVacantSpaces | integer  | 1           | realtime_free_capacity   |                                        |
| parkingOccupancy.parkingOccupancy            | numeric  | ?           |                          | occupancy in percent, not used         |


## Enumerations

### UrbanParkingSiteType

Mapped to `type`, as `parkingLayout` is not set. Any other value falls back to `OTHER`.

| Key              | Mapping                   |
|------------------|---------------------------|
| onStreetParking  | ON_STREET                 |
| offStreetParking | OFF_STREET_PARKING_GROUND |
| other            | OTHER                     |

### UserType

Mapped to `restrictions[].type`. Other values are ignored.

| Key         | Mapping  |
|-------------|----------|
| handicapped | DISABLED |
| disabled    | DISABLED |
| families    | FAMILY   |
| women       | WOMEN    |
