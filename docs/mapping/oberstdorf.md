# Markt Oberstdorf

The Markt Oberstdorf publishes a Datex II `ParkingFacilityTablePublication` with its parking grounds, provided via the
[Mobilithek](https://mobilithek.info/offers/646664714287235072). A parking site is represented by a `parkingFacility`.
For each `parkingFacility` a `ParkingSite` is generated using the generic classes `ParkingFacilityMixin` for static data
and `ParkingFacilityStatusMixin` for realtime data.

Static values:

* `purpose` is always `CAR`
* `has_realtime_data` is always `true`
* `operator_name` is not set, as `owner.contactName` is always empty
* no restrictions are generated, as all assigned parking spaces for specific audiences have `0` spaces

| Datex II field                   | Type                                            | Cardinality | Mapping                | Comment                                                            |
|----------------------------------|-------------------------------------------------|-------------|------------------------|--------------------------------------------------------------------|
| @id                              | string                                          | 1           | uid                    |                                                                    |
| @version                         | string                                          | 1           |                        | always `1.0`                                                       |
| parkingFacilityName.values.value | string                                          | 1           | name                   |                                                                    |
| parkingFacilityRecordVersionTime | datetime                                        | 1           | static_data_updated_at | converted to UTC                                                   |
| parkingFacilityLayout            | [FacilityLayout](#FacilityLayout)               | 1           | type                   | always `singleLevel`                                               |
| totalParkingCapacity             | integer                                         | 1           | capacity               |                                                                    |
| totalParkingCapacityShortTerm    | integer                                         | 1           |                        | not used, as `totalParkingCapacity` is given                       |
| totalParkingCapacityLongTerm     | integer                                         | 1           |                        | always `0`, not used                                               |
| openingTimes                     | object                                          | 1           |                        | one `period` per weekday with `periodName` like `Monday`, not used |
| facilityLocation                 | [facilityLocation](#facilityLocation)           | 1           |                        |                                                                    |
| owner.contactName                | string                                          | 1           | operator_name          | always empty                                                       |
| assignedParkingSpaces            | [assignedParkingSpaces](#assignedParkingSpaces) | *           | restrictions           |                                                                    |

### facilityLocation

| Datex II field               | Type    | Cardinality | Mapping | Comment                   |
|------------------------------|---------|-------------|---------|---------------------------|
| @type                        | enum    | 1           |         | `xsi:type`, always `Area` |
| locationForDisplay.latitude  | numeric | 1           | lat     |                           |
| locationForDisplay.longitude | numeric | 1           | lon     |                           |

### assignedParkingSpaces

Each `assignedParkingSpaces` element contains another `assignedParkingSpaces` element. A restriction is generated for
each description with a mapping in [personTypeForWhichSpacesAssigned](#personTypeForWhichSpacesAssigned) and more than
`0` spaces.

| Datex II field                                                                                                    | Type                                                                  | Cardinality | Mapping                 | Comment                                                        |
|-------------------------------------------------------------------------------------------------------------------|-----------------------------------------------------------------------|-------------|-------------------------|----------------------------------------------------------------|
| @index                                                                                                            | integer                                                               | 1           |                         |                                                                |
| assignedParkingSpaces.numberOfAssignedParkingSpaces                                                               | integer                                                               | 1           | restrictions[].capacity | `0` for all specific audiences, so no restriction is generated |
| assignedParkingSpaces.descriptionOfAssignedParkingSpaces.parkingDuration                                          | enum                                                                  | ?           |                         | `shortTerm` or `longTerm`, not used                            |
| assignedParkingSpaces.descriptionOfAssignedParkingSpaces.personTypeForWhichSpacesAssigned                         | [personTypeForWhichSpacesAssigned](#personTypeForWhichSpacesAssigned) | ?           | restrictions[].type     | `disabled`, `women` or `families`                              |
| assignedParkingSpaces.descriptionOfAssignedParkingSpaces.characteristicsOfVehiclesForWhichSpacesAssigned.fuelType | enum                                                                  | ?           | restrictions[].type     | always `battery`, mapped to `CHARGING`                         |

## Realtime data

Realtime data is provided in a separate Datex II `ParkingFacilityTableStatusPublication`. Each `parkingFacilityStatus`
references a `parkingFacility` by id.

| Datex II field                        | Type                                            | Cardinality | Mapping                  | Comment                                                       |
|---------------------------------------|-------------------------------------------------|-------------|--------------------------|---------------------------------------------------------------|
| parkingFacilityReference.@id          | string                                          | 1           | uid                      | matched against the static `parkingFacility` id               |
| parkingFacilityReference.@targetClass | string                                          | 1           |                          | always `ParkingFacility`                                      |
| parkingFacilityReference.@version     | string                                          | 1           |                          | always `1.0`                                                  |
| parkingFacilityStatusTime             | datetime                                        | 1           | realtime_data_updated_at | converted to UTC                                              |
| parkingFacilityStatus                 | [ParkingFacilityStatus](#ParkingFacilityStatus) | *           | realtime_opening_status  | always `open` and `spacesAvailable`                           |
| totalNumberOfVacantParkingSpaces      | integer                                         | 1           | realtime_free_capacity   |                                                               |
| totalNumberOfOccupiedParkingSpaces    | integer                                         | 1           |                          | not used                                                      |
| assignedParkingSpacesStatus           | object                                          | 1           |                          | occupied and vacant spaces of the short term spaces, not used |

`realtime_capacity` is not set, as the realtime data has no capacity override.

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

### personTypeForWhichSpacesAssigned

Mapped to `restrictions[].type`, if the description contains nothing else. Additionally, a description with just
`characteristicsOfVehiclesForWhichSpacesAssigned.fuelType` `battery` is mapped to `CHARGING`.

| Key      | Mapping  |
|----------|----------|
| disabled | DISABLED |
| women    | WOMEN    |
| families | FAMILY   |

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
