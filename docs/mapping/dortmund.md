# Stadt Dortmund

The city of Dortmund publishes its parking facilities as Datex II v2 `ParkingFacilityTablePublication` (static data)
and `ParkingFacilityTableStatusPublication` (realtime data) via the
[Mobilithek](https://mobilithek.info/offers/555358777795076096). Both documents are wrapped in the Mobilithek container
format (`container/body/xml`), which is unwrapped before the import. Each `parkingFacility` becomes a `ParkingSite`,
using the generic classes `ParkingFacilityMixin` and `ParkingFacilityStatusMixin`.

**Invalid DATEX II:** all parking facilities have an empty `owner` element, although an owner requires a
`contactName`. These empty elements are treated as missing owner, so the data is imported nevertheless.

Static values:

* `purpose` is always `CAR`
* `has_realtime_data` is always `true`
* parking facilities in `parkingFacilityTable.parkingFacility` and in `parkingFacilityTable.parkingArea.parkingFacility`
  are imported

## Static data

| Datex II field                     | Type                                            | Cardinality | Mapping                | Comment                                                                          |
|------------------------------------|-------------------------------------------------|-------------|------------------------|----------------------------------------------------------------------------------|
| @id                                | string                                          | 1           | uid                    |                                                                                  |
| @version                           | string                                          | 1           |                        | always `1.0`                                                                     |
| parkingFacilityLayout              | [FacilityLayout](#FacilityLayout)               | ?           | type                   | always `singleLevel`; `OTHER` if missing                                         |
| parkingFacilityName.values.value   | string                                          | 1           | name                   | German value preferred, otherwise the first value                                |
| parkingFacilityRecordVersionTime   | datetime                                        | 1           | static_data_updated_at | without timezone, `Europe/Berlin` is assumed                                     |
| totalParkingCapacity               | integer                                         | ?           | capacity               |                                                                                  |
| totalParkingCapacityShortTerm      | integer                                         | ?           | capacity               | only used if `totalParkingCapacity` is missing: short term + long term           |
| totalParkingCapacityLongTerm       | integer                                         | ?           | capacity               | only used if `totalParkingCapacity` is missing: short term + long term, always 0 |
| openingTimes.period                | object                                          | *           |                        | one period per weekday with `startOfPeriod`, `endOfPeriod` and `periodName`      |
| facilityLocation                   | [facilityLocation](#facilityLocation)           | 1           | lat, lon               |                                                                                  |
| owner                              | [owner](#owner)                                 | ?           | operator_name          | always empty                                                                     |
| characteristicsOfPermittedVehicles | [heightCharacteristic](#heightCharacteristic)   | ?           | max_height             | not present in the data                                                          |
| assignedParkingSpaces              | [assignedParkingSpaces](#assignedParkingSpaces) | *           | restrictions           |                                                                                  |

### facilityLocation

| Datex II field               | Type    | Cardinality | Mapping  | Comment                                                                      |
|------------------------------|---------|-------------|----------|------------------------------------------------------------------------------|
| @type                        | enum    | 1           |          | `xsi:type`, always `Area`                                                    |
| locationForDisplay.latitude  | numeric | ?           | lat      | used for `Area`                                                              |
| locationForDisplay.longitude | numeric | ?           | lon      | used for `Area`                                                              |
| pointByCoordinates           | object  | ?           | lat, lon | used for `Point` if `locationForDisplay` is missing, not present in the data |

### owner

| Datex II field | Type   | Cardinality | Mapping       | Comment                                     |
|----------------|--------|-------------|---------------|---------------------------------------------|
| contactName    | string | ?           | operator_name | the `owner` element is always empty instead |

### heightCharacteristic

Only used if `comparisonOperator` is `lessThan` or `lessThanOrEqualTo`.

| Datex II field                          | Type    | Cardinality | Mapping    | Comment                          |
|-----------------------------------------|---------|-------------|------------|----------------------------------|
| heightCharacteristic.comparisonOperator | enum    | 1           |            |                                  |
| heightCharacteristic.vehicleHeight      | numeric | 1           | max_height | meters, converted to centimeters |

### assignedParkingSpaces

Every `assignedParkingSpaces` with a known audience and more than 0 spaces becomes a restriction. In the data, all
assigned spaces with a known audience have 0 spaces, so no restrictions are created.

| Datex II field                                           | Type    | Cardinality | Mapping                 | Comment                                             |
|----------------------------------------------------------|---------|-------------|-------------------------|-----------------------------------------------------|
| @index                                                   | integer | 1           |                         |                                                     |
| assignedParkingSpaces.numberOfAssignedParkingSpaces      | integer | 1           | restrictions[].capacity | assigned spaces with `0` are skipped                |
| assignedParkingSpaces.descriptionOfAssignedParkingSpaces | object  | 1           | restrictions[].type     | see [AssignedParkingSpaces](#AssignedParkingSpaces) |

## Realtime data

Each `parkingFacilityStatus` references a `parkingFacility` by id. If a source publishes several states for the same
parking facility, their capacities are added up, but Dortmund publishes one state per parking facility.

| Datex II field                     | Type                                            | Cardinality | Mapping                  | Comment                                                     |
|------------------------------------|-------------------------------------------------|-------------|--------------------------|-------------------------------------------------------------|
| parkingFacilityReference.@id       | string                                          | 1           | uid                      | matched against the static `parkingFacility` id             |
| parkingFacilityStatus              | [ParkingFacilityStatus](#ParkingFacilityStatus) | *           | realtime_opening_status  | two values, e.g. `spacesAvailable` and `open`               |
| parkingFacilityStatusTime          | datetime                                        | 1           | realtime_data_updated_at | without timezone, `Europe/Berlin` is assumed                |
| totalNumberOfOccupiedParkingSpaces | integer                                         | ?           |                          |                                                             |
| totalNumberOfVacantParkingSpaces   | integer                                         | ?           | realtime_free_capacity   |                                                             |
| totalParkingCapacityOverride       | integer                                         | ?           | realtime_capacity        | not present in the data                                     |
| assignedParkingSpacesStatus        | object                                          | *           |                          | occupied and vacant spaces per assigned parking space group |

## Enumerations

### FacilityLayout

Mapped to `type`. Any other or missing value becomes `OTHER`.

| Key                       | Mapping     |
|---------------------------|-------------|
| multiStorey               | CAR_PARK    |
| singleLevel               | CAR_PARK    |
| underground               | UNDERGROUND |
| undergroundAndMultistorey | CAR_PARK    |
| automatedParkingGarage    | CAR_PARK    |

### AssignedParkingSpaces

Mapped to `restrictions[].type`. Any other description (e.g. `parkingDuration` `shortTerm` or `longTerm`) is ignored.

| Key                                                                | Mapping  |
|--------------------------------------------------------------------|----------|
| personTypeForWhichSpacesAssigned `women`                           | WOMEN    |
| personTypeForWhichSpacesAssigned `families`                        | FAMILY   |
| personTypeForWhichSpacesAssigned `disabled`                        | DISABLED |
| characteristicsOfVehiclesForWhichSpacesAssigned.fuelType `battery` | CHARGING |

### ParkingFacilityStatus

Mapped to `realtime_opening_status`. `open` takes precedence over `closed`, `closed` over `statusUnknown`. Without any
of these values, `realtime_opening_status` is not set.

| Key             | Mapping |
|-----------------|---------|
| open            | OPEN    |
| closed          | CLOSED  |
| statusUnknown   | UNKNOWN |
| spacesAvailable |         |
