# Technische Betriebe Offenburg

The Technische Betriebe Offenburg publish the car parks of Offenburg as Datex II `ParkingTablePublication` via the
[Mobilithek](https://mobilithek.info/offers/978250862019141632). A parking site is represented by a `parkingRecord` of
type `UrbanParkingSite`. For each `parkingRecord` a `ParkingSite` is generated using the generic class
`UrbanParkingSiteMixin`. Realtime data is provided in a separate Datex II `ParkingStatusPublication` and handled by the
generic class `ParkingRecordStatusMixin`.

Some parking records have no `parkingNumberOfSpaces`. Their realtime data reports a capacity of `0` as well. They are
ignored per default, which can be disabled with the config key `PARK_API_OFFENBURG_IGNORE_MISSING_CAPACITIES` (default
`true`). If they are ignored, the realtime import fetches the static data as well and skips the realtime data of these
parking sites, so no realtime data for not existing parking sites is imported. If they are not ignored, they fail the
validation, as `capacity` is required.

Static values:

* `purpose` is always `CAR`
* `type` is always `CAR_PARK` (derived from `parkingLayout`, which is always `multiStorey`)
* `has_realtime_data` is always `true`

| Datex II field           | Type                                          | Cardinality | Mapping                | Comment                                          |
|--------------------------|-----------------------------------------------|-------------|------------------------|--------------------------------------------------|
| @type                    | enum                                          | 1           |                        | `xsi:type`, always `UrbanParkingSite`            |
| @id                      | string                                        | 1           | uid                    | e.g. `PH09`                                      |
| @version                 | string                                        | 1           |                        |                                                  |
| parkingName.values.value | string                                        | 1           | name                   | German value (`lang="de"`)                       |
| parkingRecordVersionTime | datetime                                      | 1           | static_data_updated_at |                                                  |
| parkingNumberOfSpaces    | integer                                       | ?           | capacity               | parking sites without it are ignored per default |
| parkingLocation          | [parkingLocation](#parkingLocation)           | 1           |                        |                                                  |
| parkingLayout            | [ParkingLayout](#ParkingLayout)               | 1           | type                   | always `multiStorey`                             |
| openingTimes             | object                                        | 1           |                        | always from `00:00:00` to `00:00:00`, not used   |
| urbanParkingSiteType     | [UrbanParkingSiteType](#UrbanParkingSiteType) | 1           | type                   | always `offStreetParking`                        |

### parkingLocation

| Datex II field             | Type    | Cardinality | Mapping | Comment                    |
|----------------------------|---------|-------------|---------|----------------------------|
| @type                      | enum    | 1           |         | `xsi:type`, always `Point` |
| pointCoordinates.latitude  | numeric | 1           | lat     |                            |
| pointCoordinates.longitude | numeric | 1           | lon     |                            |


## Realtime data

Each `parkingRecordStatus` references a `parkingRecord` by id. The realtime data of parking sites ignored by the static
import is skipped, see above.

| Datex II field                                 | Type                                                  | Cardinality | Mapping                  | Comment                                      |
|------------------------------------------------|-------------------------------------------------------|-------------|--------------------------|----------------------------------------------|
| @type                                          | enum                                                  | 1           |                          | `xsi:type`, always `ParkingSiteStatus`       |
| parkingRecordReference.@id                     | string                                                | 1           | uid                      |                                              |
| parkingStatusOriginTime                        | datetime                                              | ?           | realtime_data_updated_at | defaults to import time if absent            |
| parkingOccupancy.parkingNumberOfSpacesOverride | integer                                               | 1           | realtime_capacity        | `0` at parking sites without static capacity |
| parkingOccupancy.parkingNumberOfVacantSpaces   | integer                                               | 1           | realtime_free_capacity   |                                              |
| parkingOccupancy.parkingNumberOfOccupiedSpaces | integer                                               | 1           |                          | not used, as vacant spaces are given         |
| parkingOccupancy.parkingNumberOfVehicles       | integer                                               | 1           |                          | not used                                     |
| parkingOccupancy.parkingOccupancy              | numeric                                               | 1           |                          | occupancy in percent, not used               |
| parkingOccupancy.parkingOccupancyTrend         | enum                                                  | ?           |                          | always `stable`, not used                    |
| parkingOccupancy.vehicleCountAndRate           | object                                                | 1           |                          | incoming and outgoing vehicles, not used     |
| overrideParkingThresholds                      | object                                                | ?           |                          | occupancy thresholds, not used               |
| parkingSiteStatus                              | enum                                                  | 1           |                          | `spacesAvailable` or `unknown`, not used     |
| parkingSiteOpeningStatus                       | [ParkingSiteOpeningStatus](#ParkingSiteOpeningStatus) | 1           | realtime_opening_status  | always `open`                                |


## Enumerations

### ParkingLayout

Mapped to `type`, unless `urbanParkingSiteType` is `onStreetParking`. Other values fall back to the type of
`urbanParkingSiteType`.

| Key                       | Mapping                   |
|---------------------------|---------------------------|
| multiStorey               | CAR_PARK                  |
| underground               | UNDERGROUND               |
| undergroundAndMultiStorey | CAR_PARK                  |
| automatedParkingGarage    | CAR_PARK                  |
| singleLevel               | OFF_STREET_PARKING_GROUND |
| covered                   | OFF_STREET_PARKING_GROUND |
| field                     | OFF_STREET_PARKING_GROUND |

### UrbanParkingSiteType

`onStreetParking` always results in `ON_STREET`. Otherwise it is used if `parkingLayout` does not give a type, and if
this does not give a type either, `type` is `OTHER`.

| Key              | Mapping                   |
|------------------|---------------------------|
| onStreetParking  | ON_STREET                 |
| offStreetParking | OFF_STREET_PARKING_GROUND |

### ParkingSiteOpeningStatus

Mapped to `realtime_opening_status`. Any other value leaves `realtime_opening_status` empty.

| Key            | Mapping |
|----------------|---------|
| open           | OPEN    |
| closed         | CLOSED  |
| closedAbnormal | CLOSED  |
| statusUnknown  | UNKNOWN |
