# Stadt Erfurt

The city of Erfurt publishes a Datex II `ParkingFacilityTablePublication` with its car parks, provided via the
[Mobilithek](https://mobilithek.info/offers/110000000002746001). A parking site is represented by a `parkingFacility`.
For each `parkingFacility` a `ParkingSite` is generated using the generic classes `ParkingFacilityMixin` for static data
and `ParkingFacilityStatusMixin` for realtime data.

**Invalid DATEX II:** the static and realtime documents lack the required `exchange` element. The converter just checks
the root element, so the data is imported nevertheless.

Static values:

* `purpose` is always `CAR`
* `has_realtime_data` is always `true`

| Datex II field                   | Type                                  | Cardinality | Mapping                | Comment                                                   |
|----------------------------------|---------------------------------------|-------------|------------------------|-----------------------------------------------------------|
| @id                              | string                                | 1           | uid                    |                                                           |
| parkingFacilityDescription       | string                                | 1           |                        | number and name, e.g. `PH08: Forum 2+3`, not used         |
| parkingFacilityName.values.value | string                                | 1           | name                   |                                                           |
| parkingFacilityRecordVersionTime | datetime                              | 1           | static_data_updated_at | converted to UTC                                          |
| parkingFacilityLayout            | [FacilityLayout](#FacilityLayout)     | 1           | type                   | always `multiStorey`                                      |
| totalParkingCapacity             | integer                               | 1           | capacity               |                                                           |
| totalParkingCapacityShortTerm    | integer                               | 1           |                        | not used, as `totalParkingCapacity` is given              |
| totalParkingCapacityLongTerm     | integer                               | ?           |                        | not used, as `totalParkingCapacity` is given              |
| openingTimes                     | object                                | 1           |                        | `openAllYear` and a `period` of the current day, not used |
| facilityLocation                 | [facilityLocation](#facilityLocation) | 1           |                        |                                                           |

### facilityLocation

| Datex II field                                | Type    | Cardinality | Mapping | Comment                    |
|-----------------------------------------------|---------|-------------|---------|----------------------------|
| @type                                         | enum    | 1           |         | `xsi:type`, always `Point` |
| pointByCoordinates.pointCoordinates.latitude  | numeric | 1           | lat     |                            |
| pointByCoordinates.pointCoordinates.longitude | numeric | 1           | lon     |                            |

## Realtime data

Realtime data is provided in a separate Datex II `ParkingFacilityTableStatusPublication`. Each `parkingFacilityStatus`
references a `parkingFacility` by id. Parking facilities with short and long term spaces have one
`parkingFacilityStatus` per capacity type.

| Datex II field                        | Type                                            | Cardinality | Mapping                  | Comment                                         |
|---------------------------------------|-------------------------------------------------|-------------|--------------------------|-------------------------------------------------|
| parkingFacilityReference.@id          | string                                          | 1           | uid                      | matched against the static `parkingFacility` id |
| parkingFacilityReference.@version     | string                                          | 1           |                          | always `ef_parking_v1.0`                        |
| parkingFacilityStatusTime             | datetime                                        | 1           | realtime_data_updated_at | converted to UTC                                |
| parkingFacilityStatus                 | [ParkingFacilityStatus](#ParkingFacilityStatus) | *           | realtime_opening_status  | always `open`                                   |
| totalNumberOfVacantParkingSpaces      | integer                                         | 1           | realtime_free_capacity   |                                                 |
| totalNumberOfOccupiedParkingSpaces    | integer                                         | 1           |                          | not used                                        |
| totalParkingCapacityShortTermOverride | integer                                         | ?           | realtime_capacity        | capacity of the short term status               |
| totalParkingCapacityLongTermOverride  | integer                                         | ?           | realtime_capacity        | capacity of the long term status                |
| parkingFacilityOccupancy              | numeric                                         | 1           |                          | occupancy, not used                             |
| parkingFacilityOccupancyTrend         | enum                                            | 1           |                          | not used                                        |
| parkingFacilityFillRate               | integer                                         | 1           |                          | not used                                        |
| parkingFacilityExitRate               | integer                                         | 1           |                          | not used                                        |

If there are multiple `parkingFacilityStatus` for the same parking facility, e.g. one per capacity type, they are
merged: `realtime_capacity` and `realtime_free_capacity` are summed up (and stay empty if one of the partial values is
missing), and the latest `parkingFacilityStatusTime` is used.

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
