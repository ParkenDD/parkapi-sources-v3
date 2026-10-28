# LBV.SH: LKW-Stellplätze auf BAB-Rastanlagen in Schleswig-Holstein

The Landesbetrieb Straßenbau und Verkehr Schleswig-Holstein (LBV.SH) publishes truck parking spaces at motorway rest
areas in Schleswig-Holstein as Datex II `ParkingTablePublication` via the
[Mobilithek](https://mobilithek.info/offers/748478832668725248). The publications are delivered in the Mobilithek
container format, which wraps the Datex II document in `container/body/xml`; the converter unwraps it before the import.
A parking site is represented by a `parkingRecord` of type `InterUrbanParkingSite`. For each `parkingRecord` a
`ParkingSite` is generated using the generic class `InterUrbanParkingSiteMixin`. Realtime data is provided in a separate
Datex II `ParkingStatusPublication` and handled by the generic class `ParkingRecordStatusMixin`.

**Broken:** the `parkingLocation` of the static data is a `Point` without `pointByCoordinates`, so the parking sites
fail the validation and no parking site is imported. The realtime data is imported, but references a parking site which
does not exist.

Static values:

* `purpose` is always `CAR`
* `type` is always `OFF_STREET_PARKING_GROUND` (derived from `interUrbanParkingSiteLocation`, which is always `other`)
* `has_realtime_data` is always `true`
* parking records with a `parkingNumberOfSpaces` of `0` are ignored

| Datex II field                | Type                                                            | Cardinality | Mapping                | Comment                                              |
|-------------------------------|-----------------------------------------------------------------|-------------|------------------------|------------------------------------------------------|
| @type                         | enum                                                            | 1           |                        | `xsi:type`, always `InterUrbanParkingSite`           |
| @id                           | string                                                          | 1           | uid                    | e.g. `deDlpa.001.eak.1.sm.SST3`                      |
| @version                      | string                                                          | 1           |                        | always `1.0`                                         |
| parkingName.values.value      | string                                                          | 1           | name                   | German value (`lang="de"`), same as `@id`            |
| parkingRecordVersionTime      | datetime                                                        | 1           | static_data_updated_at |                                                      |
| parkingNumberOfSpaces         | integer                                                         | 1           | capacity               | the parking site is ignored if `0`                   |
| operator                      | object                                                          | 1           |                        | always empty                                         |
| parkingLocation               | object                                                          | 1           | lat, lon               | `xsi:type` `Point`, but without `pointByCoordinates` |
| interUrbanParkingSiteLocation | [InterUrbanParkingSiteLocation](#InterUrbanParkingSiteLocation) | 1           | type                   | always `other`                                       |


## Realtime data

Each `parkingRecordStatus` references a `parkingRecord` by id.

| Datex II field                               | Type                                                  | Cardinality | Mapping                  | Comment                                |
|----------------------------------------------|-------------------------------------------------------|-------------|--------------------------|----------------------------------------|
| @type                                        | enum                                                  | 1           |                          | `xsi:type`, always `ParkingSiteStatus` |
| parkingRecordReference.@id                   | string                                                | 1           | uid                      |                                        |
| parkingStatusOriginTime                      | datetime                                              | ?           | realtime_data_updated_at | defaults to import time if absent      |
| parkingOccupancy.parkingNumberOfVacantSpaces | integer                                               | 1           | realtime_free_capacity   |                                        |
| parkingSiteStatus                            | enum                                                  | 1           |                          | always `unknown`, not used             |
| parkingSiteOpeningStatus                     | [ParkingSiteOpeningStatus](#ParkingSiteOpeningStatus) | 1           | realtime_opening_status  | always `statusUnknown`                 |


## Enumerations

### InterUrbanParkingSiteLocation

Mapped to `type`. Any other or missing value falls back to `OFF_STREET_PARKING_GROUND`.

| Key            | Mapping                   |
|----------------|---------------------------|
| motorway       | OFF_STREET_PARKING_GROUND |
| nearbyMotorway | OFF_STREET_PARKING_GROUND |
| layBy          | OFF_STREET_PARKING_GROUND |
| onStreet       | ON_STREET                 |
| other          | OFF_STREET_PARKING_GROUND |

### ParkingSiteOpeningStatus

Mapped to `realtime_opening_status`. Any other value leaves `realtime_opening_status` empty.

| Key            | Mapping |
|----------------|---------|
| open           | OPEN    |
| closed         | CLOSED  |
| closedAbnormal | CLOSED  |
| statusUnknown  | UNKNOWN |
