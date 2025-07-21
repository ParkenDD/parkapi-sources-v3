# Friedrichshafen: sensor based data

Friedrichshafen uses sensors to monitor some of their disabled parking spaces. They use the
ParkingRecord / ParkingRecordStatus data model for publishing these datasets. As ParkingRecord and ParkingOccupancy
are data models for parking sites, the mapping comes with some extra work, as we have to map it to single parking
spots.

Attributes which are set statically:

* `has_realtime_data` is always set to `true`
* `purpose` is always set to `CAR`


## ParkingRecord

A `ParkingRecord` provides static data for a `ParkingSpot`.

| Field                      | Type                                                  | Cardinality | Mapping                | Comment                                                 |
|----------------------------|-------------------------------------------------------|-------------|------------------------|---------------------------------------------------------|
| id                         | string                                                | 1           | uid                    |                                                         |
| version                    | integer                                               | 1           |                        |                                                         |
| parkingName                | string                                                | 1           | name                   |                                                         |
| parkingRecordVersionTime   | string (datetime)                                     | 1           | static_data_updated_at |                                                         |
| parkingNumberOfSpaces      | integer                                               | 1           |                        | Has to be 1 at all times, will be validated             |
| parkingLocation            | [PointByCoordinates](#PointByCoordinates)             | 1           |                        |                                                         |
| assignedParkingAmongOthers | [ApplicableForUser](#ApplicableForUser)               | 1           | restricted_to.type     |                                                         |
| parkingLayout              | [ParkingLayoutEnum](#ParkingLayoutEnum)               | *           | type                   |                                                         |
| openingTimes               | Validity                                              | 1           | restricted_to.hours    | Transform to OSM 24/7, as there are just 24/7 datasets. |
| urbanParkingSiteType       | [UrbanParkingSiteTypeEnum](#UrbanParkingSiteTypeEnum) | 1           | type                   | If type is not onStreet, parkingLayout is used          |


#### ApplicableForUser

| Key      | Mapping   |
|----------|-----------|
| disabled | DISABLED  |


### ParkingLayoutEnum

| Key                       | Mapping                   |
|---------------------------|---------------------------|
| multiStorey               | CAR_PARK                  |
| singleLevel               | OFF_STREET_PARKING_GROUND |
| underground               | UNDERGROUND               |
| undergroundAndMultiStorey | CAR_PARK                  |
| automatedParkingGarage    | CAR_PARK                  |
| openSpace                 |                           |
| covered                   |                           |
| nested                    |                           |
| field                     | OFF_STREET_PARKING_GROUND |
| unknown                   |                           |
| other                     |                           |


### UrbanParkingSiteTypeEnum

| Key                 | Mapping                   |
|---------------------|---------------------------|
| onStreetParking     | ON_STREET                 |
| offStreetParking    | OFF_STREET_PARKING_GROUND |
| other               |                           |



### PointByCoordinates

| Field     | Type             | Cardinality | Mapping | Comment |
|-----------|------------------|-------------|---------|---------|
| latitude  | string (decimal) | 1           | lat     |         |
| longitude | string (decimal) | 1           | lon     |         |


## ParkingRecordStatus

`ParkingRecordStatus` provides realtime data for a `ParkingSpot`.

| Field                   | Type                                              | Cardinality | Mapping                  | Comment |
|-------------------------|---------------------------------------------------|-------------|--------------------------|---------|
| parkingRecordReference  | [ParkingRecordReference](#ParkingRecordReference) | 1           | uid                      |         |
| parkingStatusOriginTime | string (datetime)                                 | 1           | realtime_data_updated_at |         |
| parkingOccupancy        | [ParkingOccupancy](#ParkingOccupancy)             | 1           |                          |         |


### ParkingRecordReference

| Field   | Type    | Cardinality | Mapping                | Comment |
|---------|---------|-------------|------------------------|---------|
| id      | string  | 1           | uid                    |         |
| version | integer | 1           |                        |         |


### ParkingOccupancy

| Field                         | Type                       | Cardinality | Mapping         | Comment                                  |
|-------------------------------|----------------------------|-------------|-----------------|------------------------------------------|
| parkingNumberOfSpacesOverride | integer                    | 1           |                 |                                          |
| parkingNumberOfVacantSpaces   | integer                    | 1           | realtime_status | `1` means `AVAILABLE`, `0` means `TAKEN` |
| parkingNumberOfOccupiedSpaces | integer                    | 1           |                 |                                          |
| parkingNumberOfVehicles       | integer                    | 1           |                 |                                          |
| parkingOccupancy              | integer                    | 1           |                 |                                          |
| parkingOccupancyTrend         | string                     | 1           |                 |                                          |
| vehicleCountAndRate           | VehicleCountAndRate        | 1           |                 |                                          |
| overrideParkingThresholds     | OverrideParkingThresholds  | 1           |                 |                                          |
| parkingSiteStatus             | ParkingSiteStatusExtension | 1           |                 |                                          |
| parkingSiteOpeningStatus      | string                     | 1           |                 |                                          |
| parkingSiteStatusExtension    | string                     | 1           |                 |                                          |
