# Bundesautobahn truck rest areas

Toll Collect publishes a large Datex II `ParkingTablePublication` with truck parking spaces (mostly rest areas)
along the German motorways, provided via the Mobilithek. A parking space is represented by a `parkingRecord` of type
`InterUrbanParkingSite`. For each `parkingRecord` a `ParkingSite` is generated using the generic
`InterUrbanParkingSiteMixin`.

Static values:

* `purpose` is always `CAR`
* `type` is always `OFF_STREET_PARKING_GROUND` (derived from `interUrbanParkingSiteLocation`, which is always `motorway`)
* `has_realtime_data` is always `true`
* parking records with a `parkingNumberOfSpaces` of `0` are ignored
* `restrictions[0].type` is always `TRUCK`

| Datex II field                 | Type                                                            | Cardinality | Mapping                | Comment                                                  |
|--------------------------------|-----------------------------------------------------------------|-------------|------------------------|----------------------------------------------------------|
| @type                          | enum                                                            | 1           |                        | `xsi:type`, always `InterUrbanParkingSite`               |
| @id                            | string                                                          | 1           | uid                    |                                                          |
| @version                       | string                                                          | 1           |                        | e.g. `2026-06-01-1`                                      |
| parkingName.values.value       | string                                                          | 1           | name                   | German value (`lang="de"`)                               |
| parkingRecordVersionTime       | datetime                                                        | 1           | static_data_updated_at |                                                          |
| parkingNumberOfSpaces          | integer                                                         | 1           | capacity               | the parking site is ignored if `0`                       |
| parkingOccupanyDetectionType   | enum                                                            | 1           |                        | always `modelBased`                                      |
| operator                       | [operator](#operator)                                           | 1           |                        |                                                          |
| parkingLocation                | [parkingLocation](#parkingLocation)                             | 1           |                        |                                                          |
| tariffsAndPayment.freeOfCharge | boolean                                                         | 1           | has_fee                | always `true`, `has_fee = not(freeOfCharge)`             |
| parkingThresholds              | [parkingThresholds](#parkingThresholds)                         | ?           |                        | occupancy thresholds                                     |
| parkingSiteAddress             | [parkingSiteAddress](#parkingSiteAddress)                       | 1           | address                | components containing `n/a` are skipped                  |
| parkingUsageScenario           | enum                                                            | 1           |                        | always `restArea`                                        |
| parkingAccess                  | object                                                          | *           |                        | access points, `accessCategory` always `vehicleEntrance` |
| parkingStandardsAndSecurity    | [parkingStandardsAndSecurity](#parkingStandardsAndSecurity)     | 1           |                        |                                                          |
| interUrbanParkingSiteLocation  | [InterUrbanParkingSiteLocation](#InterUrbanParkingSiteLocation) | 1           | type                   | always `motorway`                                        |

### operator

| Datex II field                 | Type    | Cardinality | Mapping       | Comment                                        |
|--------------------------------|---------|-------------|---------------|------------------------------------------------|
| contactOrganisationName.values | string  | 1           | operator_name | Prefixed with `Die Autobahn GmbH des Bundes, ` |
| contactDetailsTelephoneNumber  | string  | ?           |               |                                                |
| contactDetailsEMail            | string  | ?           |               |                                                |
| urlLinkAddress                 | string  | ?           |               |                                                |
| publishingAgreement            | boolean | 1           |               | always `true`                                  |

### parkingLocation

| Datex II field             | Type    | Cardinality | Mapping | Comment                    |
|----------------------------|---------|-------------|---------|----------------------------|
| @type                      | enum    | 1           |         | `xsi:type`, always `Point` |
| pointCoordinates.latitude  | numeric | 1           | lat     |                            |
| pointCoordinates.longitude | numeric | 1           | lon     |                            |

### parkingThresholds

| Datex II field       | Type    | Cardinality | Mapping | Comment             |
|----------------------|---------|-------------|---------|---------------------|
| almostFullDecreasing | integer | ?           |         | occupancy threshold |
| almostFullIncreasing | integer | ?           |         | occupancy threshold |
| fullDecreasing       | integer | ?           |         | occupancy threshold |
| fullIncreasing       | integer | ?           |         | occupancy threshold |

### parkingSiteAddress

Assembled into `address`. Components containing `n/a` are treated as missing.

| Datex II field            | Type   | Cardinality | Mapping | Comment                                                                                 |
|---------------------------|--------|-------------|---------|-----------------------------------------------------------------------------------------|
| contactDetailsStreet      | string | ?           | address |                                                                                         |
| contactDetailsHouseNumber | string | *           | address | often `n/a` (split into single-character tags); components containing `n/a` are skipped |
| contactDetailsPostcode    | string | ?           | address |                                                                                         |
| contactDetailsCity.values | string | ?           | address |                                                                                         |
| country                   | string | ?           |         | always `de`                                                                             |

### parkingStandardsAndSecurity

| Datex II field         | Type    | Cardinality | Mapping | Comment          |
|------------------------|---------|-------------|---------|------------------|
| parkingSecurity        | enum    | 1           |         | always `unknown` |
| certifiedSecureParking | boolean | 1           |         | always `false`   |

## Realtime data

Realtime data is provided in a separate Datex II `ParkingStatusPublication`. Each `parkingRecordStatus` references a
`parkingRecord` by id and reports the number of occupied spaces, but no total capacity. Therefore the static data is
fetched alongside the realtime data and the free capacity is calculated from it.

| Datex II field                           | Type                                                  | Cardinality | Mapping                  | Comment                                                                |
|------------------------------------------|-------------------------------------------------------|-------------|--------------------------|------------------------------------------------------------------------|
| @type                                    | enum                                                  | 1           |                          | `xsi:type`, always `ParkingSiteStatus`                                 |
| parkingRecordReference.@id               | string                                                | 1           | uid                      | matched against the static `parkingRecord` id                          |
| parkingStatusOriginTime                  | datetime                                              | ?           | realtime_data_updated_at | defaults to import time if absent                                      |
| parkingOccupancy.parkingNumberOfVehicles | integer                                               | ?           | realtime_free_capacity   | `realtime_free_capacity = max(static capacity - occupied vehicles, 0)` |
| parkingOccupancy.parkingOccupancy        | numeric                                               | ?           |                          | occupancy in percent, not used                                         |
| parkingSiteStatus                        | [parkingSiteStatus](#parkingSiteStatus)               | 1           |                          | not used                                                               |
| parkingSiteOpeningStatus                 | [ParkingSiteOpeningStatus](#ParkingSiteOpeningStatus) | 1           | realtime_opening_status  |                                                                        |

The static total capacity is also passed through to `realtime_capacity`.

## Enumerations

### InterUrbanParkingSiteLocation

Mapped to `type`. Any other or missing value falls back to `OFF_STREET_PARKING_GROUND`.

| Key      | Mapping                   |
|----------|---------------------------|
| motorway | OFF_STREET_PARKING_GROUND |
| other    | OFF_STREET_PARKING_GROUND |

### ParkingSiteOpeningStatus

Mapped to `realtime_opening_status`. Any other value falls back to `UNKNOWN`.

| Key    | Mapping |
|--------|---------|
| open   | OPEN    |
| closed | CLOSED  |
| other  | UNKNOWN |

### parkingSiteStatus

Provided in the realtime data, but not used.

| Value           |
|-----------------|
| spacesAvailable |
| almostFull      |
| full            |
| unknown         |
