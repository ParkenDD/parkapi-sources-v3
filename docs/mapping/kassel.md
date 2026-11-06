# Stadt Kassel

The city of Kassel publishes a Datex II `ParkingFacilityTablePublication` with the car parks of its parking guidance
system, provided via the [Mobilithek](https://mobilithek.info/offers/110000000002249000). A parking site is represented
by a `parkingFacility`, grouped in a `parkingArea`. For each `parkingFacility` a `ParkingSite` is generated using the
generic classes `ParkingFacilityMixin` for static data and `ParkingFacilityStatusMixin` for realtime data.

Static values:

* `purpose` is always `CAR`
* `has_realtime_data` is always `true`
* `type` is always `OTHER`, as the data has no `parkingFacilityLayout`
* `uid` contains number and name of the car park, e.g. `1[Friedrichsplatz]`

| Datex II field                     | Type                                                                      | Cardinality | Mapping                | Comment                                                             |
|------------------------------------|---------------------------------------------------------------------------|-------------|------------------------|---------------------------------------------------------------------|
| @id                                | string                                                                    | 1           | uid                    |                                                                     |
| @version                           | string                                                                    | 1           |                        | always `1.0`                                                        |
| parkingFacilityDescription         | string                                                                    | 1           |                        | always empty, not used                                              |
| parkingFacilityName.values.value   | string                                                                    | 1           | name                   |                                                                     |
| parkingFacilityRecordVersionTime   | datetime                                                                  | 1           | static_data_updated_at | converted to UTC                                                    |
| totalParkingCapacity               | integer                                                                   | 1           | capacity               |                                                                     |
| totalParkingCapacityShortTerm      | integer                                                                   | 1           |                        | not used, as `totalParkingCapacity` is given                        |
| totalParkingCapacityLongTerm       | integer                                                                   | 1           |                        | not used, as `totalParkingCapacity` is given                        |
| openingTimes                       | object                                                                    | 1           |                        | `period` per weekday group with `periodName` like `Mo-Sa`, not used |
| facilityLocation                   | [facilityLocation](#facilityLocation)                                     | 1           |                        |                                                                     |
| owner.contactName                  | string                                                                    | 1           | operator_name          |                                                                     |
| characteristicsOfPermittedVehicles | [characteristicsOfPermittedVehicles](#characteristicsOfPermittedVehicles) | 1           | max_height             |                                                                     |
| assignedParkingSpaces              | [assignedParkingSpaces](#assignedParkingSpaces)                           | *           | restrictions           |                                                                     |

### facilityLocation

| Datex II field                                | Type    | Cardinality | Mapping | Comment                    |
|-----------------------------------------------|---------|-------------|---------|----------------------------|
| @type                                         | enum    | 1           |         | `xsi:type`, always `Point` |
| pointByCoordinates.pointCoordinates.latitude  | numeric | 1           | lat     |                            |
| pointByCoordinates.pointCoordinates.longitude | numeric | 1           | lon     |                            |
| externalReferencing.externalLocationCode      | string  | 1           |         | e.g. `ePOB1`, not used     |
| externalReferencing.externalReferencingSystem | string  | 1           |         | always `GIS`               |

### characteristicsOfPermittedVehicles

| Datex II field                          | Type    | Cardinality | Mapping    | Comment                                                                            |
|-----------------------------------------|---------|-------------|------------|------------------------------------------------------------------------------------|
| heightCharacteristic.comparisonOperator | enum    | 1           |            | always `lessThan`; `max_height` is only set for `lessThan` and `lessThanOrEqualTo` |
| heightCharacteristic.vehicleHeight      | numeric | 1           | max_height | in meters, converted to centimeters                                                |

### assignedParkingSpaces

Each `assignedParkingSpaces` element contains another `assignedParkingSpaces` element. A restriction is generated for
each description with a mapping in [personTypeForWhichSpacesAssigned](#personTypeForWhichSpacesAssigned) and more than
`0` spaces.

| Datex II field                                                                            | Type                                                                  | Cardinality | Mapping                 | Comment                                  |
|-------------------------------------------------------------------------------------------|-----------------------------------------------------------------------|-------------|-------------------------|------------------------------------------|
| @index                                                                                    | integer                                                               | 1           |                         |                                          |
| assignedParkingSpaces.numberOfAssignedParkingSpaces                                       | integer                                                               | 1           | restrictions[].capacity | restrictions with `0` spaces are skipped |
| assignedParkingSpaces.descriptionOfAssignedParkingSpaces.personTypeForWhichSpacesAssigned | [personTypeForWhichSpacesAssigned](#personTypeForWhichSpacesAssigned) | 1           | restrictions[].type     | `disabled` or `women`                    |

## Realtime data

Realtime data is provided in a separate Datex II `ParkingFacilityTableStatusPublication`. Each `parkingFacilityStatus`
references a `parkingFacility` by id.

| Datex II field                        | Type                                            | Cardinality | Mapping                  | Comment                                              |
|---------------------------------------|-------------------------------------------------|-------------|--------------------------|------------------------------------------------------|
| parkingFacilityReference.@id          | string                                          | 1           | uid                      | matched against the static `parkingFacility` id      |
| parkingFacilityReference.@targetClass | string                                          | 1           |                          | always `ParkingFacility`                             |
| parkingFacilityReference.@version     | string                                          | 1           |                          | always `1.0`                                         |
| parkingFacilityStatusTime             | datetime                                        | 1           | realtime_data_updated_at | converted to UTC                                     |
| parkingFacilityStatus                 | [ParkingFacilityStatus](#ParkingFacilityStatus) | *           | realtime_opening_status  | `open`, `closed` or `statusUnknown`                  |
| totalNumberOfVacantParkingSpaces      | integer                                         | 1           | realtime_free_capacity   |                                                      |
| totalNumberOfOccupiedParkingSpaces    | integer                                         | 1           |                          | not used                                             |
| totalParkingCapacityOverride          | integer                                         | 1           | realtime_capacity        |                                                      |
| totalParkingCapacityShortTermOverride | integer                                         | 1           |                          | not used, as `totalParkingCapacityOverride` is given |
| parkingFacilityOccupancy              | numeric                                         | 1           |                          | occupancy, not used                                  |

## Enumerations

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
