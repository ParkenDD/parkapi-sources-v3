# Stadt Halle (Saale)

The city of Halle (Saale) publishes a Datex II `ParkingFacilityTablePublication` with its car parks and park and ride
sites, provided via the [Mobilithek](https://mobilithek.info/offers/110000000003267000). A parking site is represented
by a `parkingFacility`. For each `parkingFacility` a `ParkingSite` is generated using the generic classes
`ParkingFacilityMixin` for static data and `ParkingFacilityStatusMixin` for realtime data.

**Invalid DATEX II:** the static and realtime documents lack the required `exchange` element. The converter just checks
the root element, so the data is imported nevertheless.

Static values:

* `purpose` is always `CAR`
* `has_realtime_data` is always `true`

| Datex II field                   | Type                                  | Cardinality | Mapping                | Comment                                                      |
|----------------------------------|---------------------------------------|-------------|------------------------|--------------------------------------------------------------|
| @id                              | string                                | 1           | uid                    |                                                              |
| parkingFacilityDescription       | string                                | 1           |                        | number and name, e.g. `PR01: Kröllwitz`, not used            |
| parkingFacilityName.values.value | string                                | 1           | name                   |                                                              |
| parkingFacilityRecordVersionTime | datetime                              | 1           | static_data_updated_at | converted to UTC                                             |
| parkingFacilityLayout            | [FacilityLayout](#FacilityLayout)     | 1           | type                   | `multiStorey` or `singleLevel`                               |
| totalParkingCapacity             | integer                               | ?           | capacity               | parking facilities without any capacity fail validation      |
| totalParkingCapacityShortTerm    | integer                               | ?           | capacity               | summed up to `capacity` if `totalParkingCapacity` is missing |
| openingTimes                     | object                                | 1           |                        | `openAllYear` and a `period` of the current day, not used    |
| facilityLocation                 | [facilityLocation](#facilityLocation) | 1           |                        |                                                              |

### facilityLocation

| Datex II field                                | Type    | Cardinality | Mapping | Comment                    |
|-----------------------------------------------|---------|-------------|---------|----------------------------|
| @type                                         | enum    | 1           |         | `xsi:type`, always `Point` |
| pointByCoordinates.pointCoordinates.latitude  | numeric | 1           | lat     |                            |
| pointByCoordinates.pointCoordinates.longitude | numeric | 1           | lon     |                            |

## Realtime data

Realtime data is provided in a separate Datex II `ParkingFacilityTableStatusPublication`. Each `parkingFacilityStatus`
references a `parkingFacility` by id.

| Datex II field                        | Type                                            | Cardinality | Mapping                  | Comment                                         |
|---------------------------------------|-------------------------------------------------|-------------|--------------------------|-------------------------------------------------|
| parkingFacilityReference.@id          | string                                          | 1           | uid                      | matched against the static `parkingFacility` id |
| parkingFacilityReference.@version     | string                                          | 1           |                          | always `hal_parking_v1.0`                       |
| parkingFacilityStatusTime             | datetime                                        | 1           | realtime_data_updated_at | converted to UTC                                |
| parkingFacilityStatus                 | [ParkingFacilityStatus](#ParkingFacilityStatus) | *           | realtime_opening_status  | always `open`                                   |
| totalNumberOfVacantParkingSpaces      | integer                                         | 1           | realtime_free_capacity   |                                                 |
| totalNumberOfOccupiedParkingSpaces    | integer                                         | 1           |                          | not used                                        |
| totalParkingCapacityShortTermOverride | integer                                         | 1           | realtime_capacity        |                                                 |
| parkingFacilityOccupancy              | numeric                                         | 1           |                          | occupancy, not used                             |
| parkingFacilityOccupancyTrend         | enum                                            | ?           |                          | not used                                        |
| parkingFacilityFillRate               | integer                                         | 1           |                          | not used                                        |
| parkingFacilityExitRate               | integer                                         | 1           |                          | not used                                        |

Realtime data is also delivered for parking facilities which fail the static validation.

## Enumerations

### FacilityLayout

Mapped to `type`. A missing `parkingFacilityLayout` results in `OTHER`.

| Key                       | Mapping     |
|---------------------------|-------------|
| multiStorey               | CAR_PARK    |
| singleLevel               | CAR_PARK    |
| underground               | UNDERGROUND |
| undergroundAndMultistorey | CAR_PARK    |
| automatedParkingGarage    | CAR_PARK    |

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
