# Landeshauptstadt Wiesbaden

The Landeshauptstadt Wiesbaden publishes a Datex II `ParkingTablePublication` with its car parks, provided via the
[Mobilithek](https://mobilithek.info/offers/110000000003166000). A parking site is represented by a `parkingRecord` of
type `UrbanParkingSite`. For each `parkingRecord` a `ParkingSite` is generated using the generic classes
`UrbanParkingSiteMixin` for static data and `ParkingRecordStatusMixin` for realtime data.

**Invalid DATEX II:** the opening times of the static data use times like `00:00` instead of `00:00:00`. As opening
times are not mapped, this does not affect the import.

Static values:

* `purpose` is always `CAR`
* `has_realtime_data` is always `true`
* `type` is derived from `urbanParkingSiteType` and `parkingLayout`, see [ParkingLayout](#ParkingLayout)
* `is_covered` is set to `true` if `parkingLayout` is `covered`

| Datex II field           | Type                                          | Cardinality | Mapping                | Comment                                           |
|--------------------------|-----------------------------------------------|-------------|------------------------|---------------------------------------------------|
| @type                    | enum                                          | 1           |                        | `xsi:type`, always `UrbanParkingSite`             |
| @id                      | string                                        | 1           | uid                    |                                                   |
| @version                 | string                                        | 1           |                        |                                                   |
| parkingName.values.value | string                                        | 1           | name                   | German value (`lang="de"`)                        |
| parkingRecordVersionTime | datetime                                      | 1           | static_data_updated_at |                                                   |
| parkingNumberOfSpaces    | integer                                       | 1           | capacity               |                                                   |
| parkingLocation          | [parkingLocation](#parkingLocation)           | 1           |                        |                                                   |
| parkingLayout            | [ParkingLayout](#ParkingLayout)               | 1           | type                   | `multiStorey` or `underground`                    |
| openingTimes             | object                                        | 1           |                        | not used; times like `00:00` are invalid DATEX II |
| urbanParkingSiteType     | [UrbanParkingSiteType](#UrbanParkingSiteType) | 1           | type                   | always `offStreetParking`                         |

### parkingLocation

| Datex II field                                | Type    | Cardinality | Mapping | Comment                    |
|-----------------------------------------------|---------|-------------|---------|----------------------------|
| @type                                         | enum    | 1           |         | `xsi:type`, always `Point` |
| pointByCoordinates.pointCoordinates.latitude  | numeric | 1           | lat     |                            |
| pointByCoordinates.pointCoordinates.longitude | numeric | 1           | lon     |                            |

## Realtime data

Realtime data is provided in a separate Datex II `ParkingStatusPublication`. Each `parkingRecordStatus` references a
`parkingRecord` by id and reports the number of occupied spaces, but no total capacity and no number of vacant spaces.
Therefore the static data is fetched alongside the realtime data and the free capacity is calculated from it.

| Datex II field                                 | Type                                                  | Cardinality | Mapping                  | Comment                                                              |
|------------------------------------------------|-------------------------------------------------------|-------------|--------------------------|----------------------------------------------------------------------|
| @type                                          | enum                                                  | 1           |                          | `xsi:type`, always `ParkingSiteStatus`                               |
| parkingRecordReference.@id                     | string                                                | 1           | uid                      | matched against the static `parkingRecord` id                        |
| parkingRecordReference.@targetClass            | string                                                | 1           |                          | always `ParkingRecord`                                               |
| parkingRecordReference.@version                | string                                                | 1           |                          |                                                                      |
| parkingStatusOriginTime                        | datetime                                              | 1           | realtime_data_updated_at | defaults to import time if absent                                    |
| parkingOccupancy.parkingNumberOfOccupiedSpaces | integer                                               | 1           | realtime_free_capacity   | `realtime_free_capacity = max(static capacity - occupied spaces, 0)` |
| parkingOccupancy.parkingNumberOfVehicles       | integer                                               | 1           |                          | not used                                                             |
| parkingOccupancy.parkingOccupancy              | numeric                                               | 1           |                          | occupancy in percent, not used                                       |
| parkingOccupancy.parkingOccupancyTrend         | enum                                                  | 1           |                          | not used                                                             |
| parkingOccupancy.vehicleCountAndRate           | object                                                | 1           |                          | vehicle counts, not used                                             |
| parkingSiteStatus                              | [parkingSiteStatus](#parkingSiteStatus)               | 1           |                          | not used                                                             |
| parkingSiteOpeningStatus                       | [ParkingSiteOpeningStatus](#ParkingSiteOpeningStatus) | 1           | realtime_opening_status  |                                                                      |

`realtime_capacity` is not set, as the realtime data has no `parkingNumberOfSpacesOverride`.

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
