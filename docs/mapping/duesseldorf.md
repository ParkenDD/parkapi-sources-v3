# Landeshauptstadt Düsseldorf

The Landeshauptstadt Düsseldorf publishes a Datex II `ParkingFacilityTablePublication` with the car parks of its parking
guidance system, provided via the [Mobilithek](https://mobilithek.info/offers/110000000002055003). A parking site is
represented by a `parkingFacility`, grouped in a `parkingArea`. For each `parkingFacility` a `ParkingSite` is generated
using the generic classes `ParkingFacilityMixin` for static data and `ParkingFacilityStatusMixin` for realtime data.

Static values:

* `purpose` is always `CAR`
* `has_realtime_data` is always `true`
* `type` is always `OTHER`, as the data has no `parkingFacilityLayout`
* `uid` contains number and name of the car park, e.g. `25[PH 25 - Talstraße]`

| Datex II field                   | Type                                  | Cardinality | Mapping                | Comment                                                      |
|----------------------------------|---------------------------------------|-------------|------------------------|--------------------------------------------------------------|
| @id                              | string                                | 1           | uid                    |                                                              |
| @version                         | string                                | 1           |                        | always `1.0`                                                 |
| parkingFacilityDescription       | string                                | 1           |                        | name without number, not used                                |
| parkingFacilityName.values.value | string                                | 1           | name                   |                                                              |
| parkingFacilityRecordVersionTime | datetime                              | 1           | static_data_updated_at | converted to UTC                                             |
| totalParkingCapacity             | integer                               | ?           | capacity               | parking facilities without any capacity fail validation      |
| totalParkingCapacityShortTerm    | integer                               | ?           | capacity               | summed up to `capacity` if `totalParkingCapacity` is missing |
| facilityLocation                 | [facilityLocation](#facilityLocation) | 1           |                        |                                                              |

### facilityLocation

| Datex II field                                | Type    | Cardinality | Mapping | Comment                    |
|-----------------------------------------------|---------|-------------|---------|----------------------------|
| @type                                         | enum    | 1           |         | `xsi:type`, always `Point` |
| pointByCoordinates.pointCoordinates.latitude  | numeric | 1           | lat     |                            |
| pointByCoordinates.pointCoordinates.longitude | numeric | 1           | lon     |                            |
| externalReferencing.externalLocationCode      | string  | 1           |         | e.g. `ePOB25`, not used    |
| externalReferencing.externalReferencingSystem | string  | 1           |         | always `GIS`               |

## Realtime data

Realtime data is provided in a separate Datex II `ParkingFacilityTableStatusPublication`. Each `parkingFacilityStatus`
references a `parkingFacility` by id.

| Datex II field                        | Type                                            | Cardinality | Mapping                  | Comment                                                |
|---------------------------------------|-------------------------------------------------|-------------|--------------------------|--------------------------------------------------------|
| parkingFacilityReference.@id          | string                                          | 1           | uid                      | matched against the static `parkingFacility` id        |
| parkingFacilityReference.@targetClass | string                                          | 1           |                          | always `ParkingFacility`                               |
| parkingFacilityReference.@version     | string                                          | 1           |                          | always `1.0`                                           |
| parkingFacilityStatusTime             | datetime                                        | 1           | realtime_data_updated_at | converted to UTC                                       |
| parkingFacilityStatus                 | [ParkingFacilityStatus](#ParkingFacilityStatus) | *           | realtime_opening_status  | `open` or `closed`                                     |
| totalNumberOfVacantParkingSpaces      | integer                                         | 1           | realtime_free_capacity   |                                                        |
| totalNumberOfOccupiedParkingSpaces    | integer                                         | 1           |                          | not used                                               |
| totalParkingCapacityOverride          | integer                                         | 1           | realtime_capacity        |                                                        |
| totalParkingCapacityShortTermOverride | integer                                         | 1           | realtime_capacity        | only used if `totalParkingCapacityOverride` is missing |
| parkingFacilityOccupancy              | numeric                                         | 1           |                          | occupancy, not used                                    |
| parkingFacilityOccupancyTrend         | enum                                            | 1           |                          | not used                                               |

## Enumerations

### ParkingFacilityStatus

`parkingFacilityStatus` can occur multiple times. The opening status is derived from the first matching value in the
order of this table; without any matching value, `realtime_opening_status` stays empty.

| Key                              | Mapping | Comment                                |
|----------------------------------|---------|----------------------------------------|
| open                             | OPEN    | takes precedence over all other values |
| closed                           | CLOSED  | takes precedence over `statusUnknown`  |
| statusUnknown                    | UNKNOWN |                                        |
| spacesAvailable                  | -       |                                        |
| almostFull                       | -       |                                        |
| fullAtEntrance                   | -       |                                        |
| full                             | -       |                                        |
| normalParkingConditionsSuspended | -       |                                        |
| specialParkingConditionsInForce  | -       |                                        |
