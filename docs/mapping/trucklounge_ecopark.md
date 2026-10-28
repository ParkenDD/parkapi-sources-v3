# ENMO: Trucklounge Ecopark

ENMO GmbH & Co.KG publishes the truck parking site Trucklounge Ecopark in Emstek as Datex II `ParkingTablePublication`
via the [Mobilithek](https://mobilithek.info/offers/953737601668071424). A parking site is represented by a
`parkingRecord` of type `InterUrbanParkingSite`. For each `parkingRecord` a `ParkingSite` is generated using the generic
class `InterUrbanParkingSiteMixin`. Realtime data is provided in a separate Datex II `ParkingStatusPublication` and
handled by the generic class `ParkingRecordStatusMixin`.

**Broken:** the static data has neither `parkingNumberOfSpaces` nor `groupOfParkingSpaces`, so there is no capacity and
the parking site fails the validation. Additionally, the static data is not valid DATEX II: latitude and longitude of
`parkingLocation` are swapped. No parking site is imported. The realtime data is imported, but references a parking site
which does not exist.

Static values:

* `purpose` is always `CAR`
* `type` is always `OFF_STREET_PARKING_GROUND` (derived from `interUrbanParkingSiteLocation`, which is always
  `nearbyMotorway`)
* `has_realtime_data` is always `true`

| Datex II field                 | Type                                                            | Cardinality | Mapping                | Comment                                                |
|--------------------------------|-----------------------------------------------------------------|-------------|------------------------|--------------------------------------------------------|
| @type                          | enum                                                            | 1           |                        | `xsi:type`, always `InterUrbanParkingSite`             |
| @id                            | string                                                          | 1           | uid                    | UUID                                                   |
| @version                       | string                                                          | 1           |                        | always `1`                                             |
| parkingName.values.value       | string                                                          | 1           | name                   | German value (`lang="de"`)                             |
| parkingRecordVersionTime       | datetime                                                        | 1           | static_data_updated_at |                                                        |
| parkingOccupanyDetectionType   | enum                                                            | 1           |                        | always `balancing`                                     |
| operator                       | [operator](#operator)                                           | 1           | operator_name          |                                                        |
| parkingLocation                | [parkingLocation](#parkingLocation)                             | 1           |                        | latitude and longitude are swapped                     |
| onlyAssignedParking            | object                                                          | 1           |                        | `vehicleCharacteristics.vehicleType` `lorry`, not used |
| tariffsAndPayment              | [tariffsAndPayment](#tariffsAndPayment)                         | 1           |                        |                                                        |
| parkingThresholds.overcrowding | integer                                                         | 1           |                        | not used                                               |
| parkingSiteAddress             | [parkingSiteAddress](#parkingSiteAddress)                       | 1           | address                |                                                        |
| parkingUsageScenario           | object                                                          | *           |                        | `truckParking` and `restArea`, not used                |
| parkingAccess                  | object                                                          | 1           |                        | entrance with barrier and roads, not used              |
| parkingStandardsAndSecurity    | object                                                          | 1           |                        | `cctv`, `fences`, `lighting` and `other`, not used     |
| interUrbanParkingSiteLocation  | [InterUrbanParkingSiteLocation](#InterUrbanParkingSiteLocation) | 1           | type                   | always `nearbyMotorway`                                |

### operator

| Datex II field                 | Type    | Cardinality | Mapping       | Comment                             |
|--------------------------------|---------|-------------|---------------|-------------------------------------|
| @type                          | enum    | 1           |               | `xsi:type`, always `ContactDetails` |
| contactOrganisationName.values | string  | 1           | operator_name |                                     |
| contactPersonName              | string  | 1           |               |                                     |
| contactPersonFirstName         | string  | 1           |               |                                     |
| contactDetailsTelephoneNumber  | string  | 1           |               |                                     |
| contactDetailsEMail            | string  | 1           |               |                                     |
| publishingAgreement            | boolean | 1           |               | always `true`                       |

### parkingLocation

| Datex II field             | Type    | Cardinality | Mapping | Comment                    |
|----------------------------|---------|-------------|---------|----------------------------|
| @type                      | enum    | 1           |         | `xsi:type`, always `Point` |
| pointCoordinates.latitude  | numeric | 1           | lat     | contains the longitude     |
| pointCoordinates.longitude | numeric | 1           | lon     | contains the latitude      |

### tariffsAndPayment

| Datex II field | Type    | Cardinality | Mapping | Comment                                                                       |
|----------------|---------|-------------|---------|-------------------------------------------------------------------------------|
| freeOfCharge   | boolean | 1           | has_fee | always `0`; `xs:boolean` `1` / `0` is accepted, `has_fee = not(freeOfCharge)` |
| urlLinkAddress | string  | 1           |         | booking URL, not used                                                         |

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
| country                   | string | 1           |         | always `de`             |


## Realtime data

Each `parkingRecordStatus` references a `parkingRecord` by id.

| Datex II field                               | Type                                                  | Cardinality | Mapping                  | Comment                                |
|----------------------------------------------|-------------------------------------------------------|-------------|--------------------------|----------------------------------------|
| @type                                        | enum                                                  | 1           |                          | `xsi:type`, always `ParkingSiteStatus` |
| parkingRecordReference.@id                   | string                                                | 1           | uid                      |                                        |
| parkingStatusOriginTime                      | datetime                                              | ?           | realtime_data_updated_at | defaults to import time if absent      |
| parkingSpaceStatus                           | object                                                | 1           |                          | status of a single space, not used     |
| parkingOccupancy.parkingNumberOfVacantSpaces | integer                                               | 1           | realtime_free_capacity   |                                        |
| parkingOccupancy.parkingNumberOfVehicles     | integer                                               | 1           |                          | not used                               |
| groupOfParkingSpacesStatus                   | object                                                | 1           |                          | same numbers per group, not used       |
| parkingSiteStatus                            | enum                                                  | 1           |                          | always `spacesAvailable`, not used     |
| parkingSiteOpeningStatus                     | [ParkingSiteOpeningStatus](#ParkingSiteOpeningStatus) | 1           | realtime_opening_status  | always `open`                          |


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
