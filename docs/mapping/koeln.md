# Stadt Köln

The city of Köln publishes a Datex II `ParkingTablePublication` with its car parks, provided via the
[Mobilithek](https://mobilithek.info/offers/110000000002898000) under the Datenlizenz Deutschland – Zero – Version 2.0.
A parking site is represented by a `parkingRecord` of type `UrbanParkingSite`. For each `parkingRecord` a `ParkingSite`
is generated using the generic classes `UrbanParkingSiteMixin` for static data and `ParkingRecordStatusMixin` for
realtime data.

Static values:

* `purpose` is always `CAR`
* `has_realtime_data` is always `true`
* `type` is derived from `urbanParkingSiteType` and `parkingLayout`, see [ParkingLayout](#ParkingLayout)
* `is_covered` is set to `true` if `parkingLayout` is `covered`

| Datex II field                  | Type                                          | Cardinality | Mapping                | Comment                                              |
|---------------------------------|-----------------------------------------------|-------------|------------------------|------------------------------------------------------|
| @type                           | enum                                          | 1           |                        | `xsi:type`, always `UrbanParkingSite`                |
| @id                             | string                                        | 1           | uid                    |                                                      |
| @version                        | string                                        | 1           |                        |                                                      |
| parkingName.values.value        | string                                        | 1           | name                   | German value (`lang="de"`)                           |
| parkingDescription.values.value | string                                        | ?           |                        | opening times as text, not used                      |
| parkingRecordVersionTime        | datetime                                      | 1           | static_data_updated_at |                                                      |
| parkingNumberOfSpaces           | integer                                       | ?           | capacity               | required, parking records without it fail validation |
| parkingLocation                 | [parkingLocation](#parkingLocation)           | 1           |                        |                                                      |
| parkingLayout                   | [ParkingLayout](#ParkingLayout)               | 1           | type                   | always `multiStorey`                                 |
| openingTimes                    | object                                        | 1           |                        | not used                                             |
| urbanParkingSiteType            | [UrbanParkingSiteType](#UrbanParkingSiteType) | 1           | type                   | always `offStreetParking`                            |

### parkingLocation

| Datex II field                                | Type    | Cardinality | Mapping | Comment                    |
|-----------------------------------------------|---------|-------------|---------|----------------------------|
| @type                                         | enum    | 1           |         | `xsi:type`, always `Point` |
| pointByCoordinates.pointCoordinates.latitude  | numeric | 1           | lat     |                            |
| pointByCoordinates.pointCoordinates.longitude | numeric | 1           | lon     |                            |

## Realtime data

Realtime data is provided in a separate Datex II `ParkingStatusPublication`. Each `parkingRecordStatus` references a
`parkingRecord` by id.

| Datex II field                                 | Type                                                  | Cardinality | Mapping                  | Comment                                             |
|------------------------------------------------|-------------------------------------------------------|-------------|--------------------------|-----------------------------------------------------|
| @type                                          | enum                                                  | 1           |                          | `xsi:type`, always `ParkingSiteStatus`              |
| parkingRecordReference.@id                     | string                                                | 1           | uid                      | matched against the static `parkingRecord` id       |
| parkingRecordReference.@targetClass            | string                                                | 1           |                          | always `ParkingRecord`                              |
| parkingRecordReference.@version                | string                                                | 1           |                          |                                                     |
| parkingStatusOriginTime                        | datetime                                              | 1           | realtime_data_updated_at | defaults to import time if absent                   |
| parkingOccupancy.parkingNumberOfSpacesOverride | integer                                               | 1           | realtime_capacity        |                                                     |
| parkingOccupancy.parkingNumberOfVacantSpaces   | integer                                               | 1           | realtime_free_capacity   |                                                     |
| parkingOccupancy.parkingNumberOfOccupiedSpaces | integer                                               | 1           |                          | not used, as `parkingNumberOfVacantSpaces` is given |
| parkingOccupancy.parkingNumberOfVehicles       | integer                                               | 1           |                          | not used                                            |
| parkingOccupancy.parkingOccupancy              | numeric                                               | 1           |                          | occupancy in percent, not used                      |
| parkingOccupancy.parkingOccupancyTrend         | enum                                                  | ?           |                          | not used                                            |
| parkingOccupancy.vehicleCountAndRate           | object                                                | 1           |                          | vehicle counts, not used                            |
| overrideParkingThresholds                      | object                                                | ?           |                          | occupancy thresholds, not used                      |
| parkingSiteStatus                              | [parkingSiteStatus](#parkingSiteStatus)               | 1           |                          | not used                                            |
| parkingSiteOpeningStatus                       | [ParkingSiteOpeningStatus](#ParkingSiteOpeningStatus) | 1           | realtime_opening_status  |                                                     |

Realtime data is also delivered for parking records which fail the static validation, with a
`parkingNumberOfSpacesOverride` of `0`.

## Enumerations

### ParkingLayout

Mapped to `type`, unless `urbanParkingSiteType` is `onStreetParking`. Values without a mapping fall back to the mapping
of `urbanParkingSiteType`.

| Key                       | Mapping                            |
|---------------------------|------------------------------------|
| multiStorey               | CAR_PARK                           |
| underground               | UNDERGROUND                        |
| undergroundAndMultiStorey | CAR_PARK                           |
| automatedParkingGarage    | CAR_PARK                           |
| singleLevel               | OFF_STREET_PARKING_GROUND          |
| covered                   | OFF_STREET_PARKING_GROUND          |
| field                     | OFF_STREET_PARKING_GROUND          |
| openSpace                 | fallback to `urbanParkingSiteType` |
| nested                    | fallback to `urbanParkingSiteType` |
| unknown                   | fallback to `urbanParkingSiteType` |
| other                     | fallback to `urbanParkingSiteType` |

### UrbanParkingSiteType

Mapped to `type` together with `parkingLayout`.

| Key              | Mapping                   | Comment                                     |
|------------------|---------------------------|---------------------------------------------|
| onStreetParking  | ON_STREET                 | overrides `parkingLayout`                   |
| offStreetParking | OFF_STREET_PARKING_GROUND | only used if `parkingLayout` has no mapping |
| other            | OTHER                     | only used if `parkingLayout` has no mapping |

### ParkingSiteOpeningStatus

Mapped to `realtime_opening_status`. Values without a mapping leave `realtime_opening_status` empty.

| Key                 | Mapping |
|---------------------|---------|
| open                | OPEN    |
| closed              | CLOSED  |
| closedAbnormal      | CLOSED  |
| statusUnknown       | UNKNOWN |
| openingTimesInForce | -       |
| other               | -       |

### parkingSiteStatus

Provided in the realtime data, but not used.

| Value           |
|-----------------|
| spacesAvailable |
| unknown         |
