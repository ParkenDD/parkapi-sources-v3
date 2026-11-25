# Hamburg Port Authority: LKW-Parkplätze Hamburger Hafen

The Hamburg Port Authority publishes truck parking sites in the port of Hamburg as Datex II `ParkingTablePublication`
via the [Mobilithek](https://mobilithek.info/offers/658426993588482048). A parking site is represented by a
`parkingRecord` of type `UrbanParkingSite`. For each `parkingRecord` a `ParkingSite` is generated using the generic
class `UrbanParkingSiteMixin`. Realtime data is provided in a separate Datex II `ParkingStatusPublication` and handled
by the generic class `ParkingRecordStatusMixin`.

Static values:

* `purpose` is always `CAR`
* `restrictions[0].type` is always `TRUCK`, as all parking sites are truck parking sites, which the urban parking site
  model cannot express
* `type` is always `CAR_PARK` (derived from `parkingLayout`, which is always `multiStorey`)
* `has_realtime_data` is always `true`

| Datex II field            | Type                                          | Cardinality | Mapping                | Comment                                        |
|---------------------------|-----------------------------------------------|-------------|------------------------|------------------------------------------------|
| @type                     | enum                                          | 1           |                        | `xsi:type`, always `UrbanParkingSite`          |
| @id                       | string                                        | 1           | uid                    |                                                |
| @version                  | string                                        | 1           |                        |                                                |
| parkingName.values.value  | string                                        | 1           | name                   | German value (`lang="de"`)                     |
| parkingDescription.values | string                                        | 1           |                        | not used                                       |
| parkingRecordVersionTime  | datetime                                      | 1           | static_data_updated_at |                                                |
| parkingNumberOfSpaces     | integer                                       | 1           | capacity               |                                                |
| parkingLocation           | [parkingLocation](#parkingLocation)           | 1           |                        |                                                |
| parkingLayout             | [ParkingLayout](#ParkingLayout)               | 1           | type                   | always `multiStorey`                           |
| openingTimes              | object                                        | 1           |                        | always from `00:00:00` to `00:00:00`, not used |
| urbanParkingSiteType      | [UrbanParkingSiteType](#UrbanParkingSiteType) | 1           | type                   | always `offStreetParking`                      |

### parkingLocation

| Datex II field             | Type    | Cardinality | Mapping | Comment                    |
|----------------------------|---------|-------------|---------|----------------------------|
| @type                      | enum    | 1           |         | `xsi:type`, always `Point` |
| pointCoordinates.latitude  | numeric | 1           | lat     |                            |
| pointCoordinates.longitude | numeric | 1           | lon     |                            |


## Realtime data

Each `parkingRecordStatus` references a `parkingRecord` by id.

| Datex II field                                 | Type                                                  | Cardinality | Mapping                  | Comment                                     |
|------------------------------------------------|-------------------------------------------------------|-------------|--------------------------|---------------------------------------------|
| @type                                          | enum                                                  | 1           |                          | `xsi:type`, always `ParkingSiteStatus`      |
| parkingRecordReference.@id                     | string                                                | 1           | uid                      |                                             |
| parkingStatusOriginTime                        | datetime                                              | ?           | realtime_data_updated_at | defaults to import time if absent           |
| parkingOccupancy.parkingNumberOfSpacesOverride | integer                                               | 1           | realtime_capacity        |                                             |
| parkingOccupancy.parkingNumberOfVacantSpaces   | integer                                               | 1           | realtime_free_capacity   |                                             |
| parkingOccupancy.parkingNumberOfOccupiedSpaces | integer                                               | 1           |                          | not used, as vacant spaces are given        |
| parkingOccupancy.parkingNumberOfVehicles       | integer                                               | 1           |                          | not used                                    |
| parkingOccupancy.parkingOccupancy              | numeric                                               | 1           |                          | occupancy in percent, not used              |
| parkingOccupancy.vehicleCountAndRate           | object                                                | 1           |                          | incoming and outgoing vehicles, not used    |
| overrideParkingThresholds                      | object                                                | 1           |                          | occupancy thresholds, not used              |
| parkingSiteStatus                              | enum                                                  | 1           |                          | `spacesAvailable` or `almostFull`, not used |
| parkingSiteOpeningStatus                       | [ParkingSiteOpeningStatus](#ParkingSiteOpeningStatus) | 1           | realtime_opening_status  | always `open`                               |


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
