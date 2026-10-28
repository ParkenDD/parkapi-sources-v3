# Stadt Frankfurt am Main

The city of Frankfurt am Main publishes its car parks as Datex II v3 `ParkingTablePublication` via the
[Mobilithek](https://mobilithek.info/offers/919987874795593728). A parking site is represented by a `parkingRecord` of
type `UrbanParkingSite`. For each `parkingRecord` a `ParkingSite` is generated using the generic class
`UrbanParkingSiteV3Mixin`. Realtime data is provided in a separate Datex II v3 `ParkingStatusPublication` and handled by
the generic class `ParkingRecordStatusV3Mixin`.

**Invalid DATEX II:** the data does not validate against its declared profile Parkraummanagement DATEX II v3:
`parkingSpaceOrGroupIdentifier` at the static data and `parkingStatusValidity` at the realtime data are not part of it.
Both fields are not needed for the mapping, so the import works anyway.

Static values:

* `purpose` is always `CAR`
* `has_realtime_data` is always `true`
* `type` is always `OTHER`, because `urbanParkingSiteType` is always `other` and `parkingLayout` is not set

| Datex II field                    | Type                                          | Cardinality | Mapping                | Comment                                              |
|-----------------------------------|-----------------------------------------------|-------------|------------------------|------------------------------------------------------|
| @type                             | enum                                          | 1           |                        | `xsi:type`, always `UrbanParkingSite`                |
| @id                               | string                                        | 1           | uid                    |                                                      |
| @version                          | string                                        | 1           |                        |                                                      |
| parkingName.values                | string                                        | 1           | name                   | German value preferred, otherwise the first value    |
| parkingAlias.values               | string                                        | ?           |                        |                                                      |
| parkingDescription.values         | string                                        | 1           | description            | always empty                                         |
| parkingRecordVersionTime          | datetime                                      | 1           | static_data_updated_at |                                                      |
| parkingNumberOfSpaces             | integer                                       | 1           | capacity               |                                                      |
| operator                          | [operator](#operator)                         | ?           |                        |                                                      |
| parkingLocation                   | [parkingLocation](#parkingLocation)           | 1           |                        |                                                      |
| tariffsAndPayment                 | [tariffsAndPayment](#tariffsAndPayment)       | 1           |                        |                                                      |
| parkingEquipmentOrServiceFacility | object                                        | *           |                        | e.g. `elevator`                                      |
| groupOfParkingSpaces              | [groupOfParkingSpaces](#groupOfParkingSpaces) | *           |                        |                                                      |
| parkingReservation                | enum                                          | 1           |                        | always `unknown`                                     |
| openingTimes                      | [openingTimes](#openingTimes)                 | 1           |                        |                                                      |
| parkingAccess                     | [parkingAccess](#parkingAccess)               | *           |                        |                                                      |
| parkingStandardsAndSecurity       | object                                        | ?           |                        | `parkingSecurity` always `none`                      |
| urbanParkingSiteType              | [UrbanParkingSiteType](#UrbanParkingSiteType) | 1           | type                   | always `other`                                       |
| onlyAssignedParking               | object                                        | ?           |                        | `vehicleCharacteristics.vehicleType` `bus`, not used |

### operator

| Datex II field                 | Type   | Cardinality | Mapping       | Comment                                           |
|--------------------------------|--------|-------------|---------------|---------------------------------------------------|
| @type                          | enum   | 1           |               | `xsi:type`, always `ContactDetails`               |
| contactOrganisationName.values | string | 1           | operator_name | German value preferred, otherwise the first value |
| contactDetailsEMail            | string | ?           |               | contains a URL instead of an email address        |

### parkingLocation

| Datex II field                                                | Type    | Cardinality | Mapping | Comment                            |
|---------------------------------------------------------------|---------|-------------|---------|------------------------------------|
| @type                                                         | enum    | 1           |         | `xsi:type`, always `PointLocation` |
| supplementaryPositionalDescription.locationDescription.values | string  | ?           |         | address                            |
| pointByCoordinates.pointCoordinates.latitude                  | numeric | 1           | lat     |                                    |
| pointByCoordinates.pointCoordinates.longitude                 | numeric | 1           | lon     |                                    |

### tariffsAndPayment

| Datex II field         | Type     | Cardinality | Mapping | Comment                       |
|------------------------|----------|-------------|---------|-------------------------------|
| lastUpdated            | datetime | 1           |         |                               |
| acceptedMeansOfPayment | enum     | *           |         | `cash`, `paymentCard`         |
| freeOfCharge           | boolean  | 1           | has_fee | `has_fee = not(freeOfCharge)` |
| chargeBand             | object   | *           |         | tariffs, not used             |
| acceptedPaymentCards   | object   | ?           |         |                               |

### groupOfParkingSpaces

Groups with `onlyAssignedParking` would be mapped to `restrictions`. The groups in the data have no
`onlyAssignedParking`, so no restrictions are created.

| Datex II field                                   | Type    | Cardinality | Mapping | Comment                          |
|--------------------------------------------------|---------|-------------|---------|----------------------------------|
| parkingSpaceBasics.@type                         | enum    | 1           |         | always `GroupOfParkingSpaces`    |
| parkingSpaceBasics.parkingSpaceOrGroupIdentifier | string  | 1           |         | not part of the declared profile |
| parkingSpaceBasics.parkingReservation            | enum    | 1           |         | always `unknown`                 |
| parkingSpaceBasics.parkingNumberOfSpaces         | integer | 1           |         | always `0`                       |
| parkingSpaceBasics.parkingTypeOfGroup            | enum    | 1           |         | always `other`                   |

### openingTimes

| Datex II field   | Type     | Cardinality | Mapping       | Comment                                         |
|------------------|----------|-------------|---------------|-------------------------------------------------|
| lastUpdated      | datetime | 1           |               |                                                 |
| available24hours | boolean  | 1           | opening_hours | always `true`, mapped to `opening_hours` `24/7` |

### parkingAccess

| Datex II field                                                    | Type   | Cardinality | Mapping    | Comment                                                                      |
|-------------------------------------------------------------------|--------|-------------|------------|------------------------------------------------------------------------------|
| @id                                                               | string | 1           |            |                                                                              |
| accessCategory                                                    | enum   | 1           |            | always `vehicleEntranceAndExit`                                              |
| accessName.values                                                 | string | 1           |            |                                                                              |
| accessOnlyAssignedFor.vehicleCharacteristics.heightCharacteristic | object | ?           | max_height | used if `comparisonOperator` is `lessThan` or `lessThanOrEqualTo`, see below |
| location.pointByCoordinates.pointCoordinates                      | object | 1           |            |                                                                              |

`max_height` is `vehicleHeight` (meters) converted to centimeters. If several accesses have a height limit, the lowest
one is used.


## Realtime data

Each `parkingRecordStatus` references a `parkingRecord` by id. Status records with `parkingStatusValidity` are forecasts
with an offset to their origin time and are ignored, so just the current status is imported.

| Datex II field                               | Type     | Cardinality | Mapping                  | Comment                                                     |
|----------------------------------------------|----------|-------------|--------------------------|-------------------------------------------------------------|
| @type                                        | enum     | 1           |                          | `xsi:type`, always `ParkingSiteStatus`                      |
| parkingRecordReference.@id                   | string   | 1           | uid                      |                                                             |
| parkingStatusOriginTime                      | datetime | ?           | realtime_data_updated_at | defaults to import time if absent                           |
| parkingOccupancy.parkingNumberOfVacantSpaces | integer  | 1           | realtime_free_capacity   | just set at the current status                              |
| parkingOccupancy.parkingOccupancy            | numeric  | ?           |                          | occupancy in percent, not used                              |
| parkingOccupancy.parkingOccupancyGraded      | enum     | 1           |                          | not used                                                    |
| parkingOccupancy._parkingOccupancyExtension  | object   | 1           |                          | occupancy bucket, not used                                  |
| parkingStatusValidity                        | object   | ?           |                          | forecast offset, status records with this field are ignored |


## Enumerations

### UrbanParkingSiteType

Mapped to `type` if `parkingLayout` does not give a type. Any other value falls back to `OTHER`.

| Key              | Mapping                   |
|------------------|---------------------------|
| onStreetParking  | ON_STREET                 |
| offStreetParking | OFF_STREET_PARKING_GROUND |
| other            | OTHER                     |
