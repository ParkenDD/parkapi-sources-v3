# Landeshauptstadt Magdeburg: ifak

The ifak e.V. publishes a Datex II `ParkingFacilityTablePublication` with car parks of Magdeburg, provided via the
[Mobilithek](https://mobilithek.info/offers/683633364717989888). A parking site is represented by a `parkingFacility`.
For each `parkingFacility` a `ParkingSite` is generated using the generic classes `ParkingFacilityMixin` for static data
and `ParkingFacilityStatusMixin` for realtime data.

**Invalid DATEX II:** the documents lack the required `modelBaseVersion` attribute, and the realtime data contains
negative numbers of occupied spaces. The converter neither checks `modelBaseVersion` nor uses the occupied spaces, so
the data is imported nevertheless.

Static values:

* `purpose` is always `CAR`
* `has_realtime_data` is always `true`
* `type` is always `OTHER`, as the data has no `parkingFacilityLayout`

| Datex II field                   | Type                                  | Cardinality | Mapping                | Comment                    |
|----------------------------------|---------------------------------------|-------------|------------------------|----------------------------|
| @id                              | string                                | 1           | uid                    |                            |
| @version                         | string                                | 1           |                        | always `1.0`               |
| parkingFacilityDescription       | string                                | 1           |                        | same as the name, not used |
| parkingFacilityName.values.value | string                                | 1           | name                   | German value (`lang="de"`) |
| parkingFacilityRecordVersionTime | datetime                              | 1           | static_data_updated_at | converted to UTC           |
| totalParkingCapacity             | integer                               | 1           | capacity               |                            |
| facilityLocation                 | [facilityLocation](#facilityLocation) | 1           |                        |                            |

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
| parkingFacilityReference.@targetClass | string                                          | 1           |                          | always `ParkingFacility`                        |
| parkingFacilityReference.@version     | string                                          | 1           |                          | always `1`                                      |
| parkingFacilityStatusTime             | datetime                                        | 1           | realtime_data_updated_at | converted to UTC                                |
| parkingFacilityStatus                 | [ParkingFacilityStatus](#ParkingFacilityStatus) | *           | realtime_opening_status  | e.g. `open` and `spacesAvailable`, or `closed`  |
| totalNumberOfVacantParkingSpaces      | integer                                         | 1           | realtime_free_capacity   |                                                 |
| totalNumberOfOccupiedParkingSpaces    | integer                                         | 1           |                          | not used; can be negative, which is invalid     |
| parkingFacilityOccupancy              | numeric                                         | 1           |                          | occupancy, not used; can be negative            |
| parkingFacilityOccupancyTrend         | enum                                            | 1           |                          | not used                                        |

`realtime_capacity` is not set, as the realtime data has no capacity override.

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
