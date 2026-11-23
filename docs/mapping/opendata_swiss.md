# Swiss Open-Data-Plattform öV Schweiz

The Swiss open transport data platform publishes the dataset **Bike and Car Parking** as a
static GeoJSON. Each feature describes exactly one parking site (car or bike parking facility).

* Only parking facilities with `properties.publicAccess: true` are integrated for Car and Bike ParkingSites
* `realtime_data_updated_at` is set to the moment of import
* `static_data_updated_at` is set to the moment of import
* `lat` and `lon` are rounded to 7 decimals


## Properties

| Field                                        | Type                                                                    | Cardinality | Mapping                   | Comment                                                                     |
|----------------------------------------------|-------------------------------------------------------------------------|-------------|---------------------------|-----------------------------------------------------------------------------|
| id                                           | string                                                                  | 1           | uid                       |                                                                                |
| geometry.geometries[].coordinates[0]         | decimal                                                                 | 1           | lon                       | `geometry.geometries[].type: Point` per feature is the site coordinate            |
| geometry.geometries[].coordinates[1]         | decimal                                                                 | 1           | lat                       | `geometry.geometries[].type: Point` per feature is the site coordinate            |
| properties.displayName                       | string                                                                  | 1           | name                      | Not unique e.g. `Veloparking Bern` appears multiple times                |
| properties.operator                          | string                                                                  | 1           | operator_name             |                                                                          |
| properties.parkingFacilityCategory           | [parkingFacilityCategory](#ParkingFacilityCategory)                     | 1           | purpose                   |                                                                        |
| properties.parkingFacilityType               | [parkingFacilityType](#ParkingFacilityType)                             | 1           | type, park_and_ride_type  |                                                                                          |
| properties.address                           | [address](#Address)                                                     | 1           | address                   | The object is always present, but `addressLine` or street address has `null` values sometimes |
| properties.capacities                        | [capacities](#Capacities)                                               | 1           | capacity, restrictions    | Has entries per restriction types and all category types with `capacities[].total > 0` is summed together as the parking sites capacity                 |
| properties.operationTime                     | [operationTime](#OperationTime)                                         | ?           | opening_hours             |                                                                       |
| properties.additionalInformationForCustomers | [additionalInformationForCustomers](#AdditionalInformationForCustomers) | ?           | description               |                                                                                 |
| properties.salesChannels                     | [salesChannels](#SalesChannels)                                         | *           | fee_description           |                                                                                  |
| properties.pricingModel                      | [pricingModel](#PricingModel)                                           | ?           | has_fee                   | If not `null` or `{}` then `has_fee: true`                                          |
| properties.bikeFacilityTraits                | [bikeFacilityTraits](#BikeFacilityTraits)                               | *           | description               | See [bikeFacilityTraits](#BikeFacilityTraits)             |
| properties.publicAccess                      | boolean                                                                 | 1           |                           | Only parking facilities with `publicAccess: true` are integrated           |
| properties.poiLevel                          | integer                                                                 | 1           | type                      | Hierarchy level e.g. `-1` = `type: UNDERGROUND`           |
| properties.temporaryInformationForCustomers  | [temporaryInformationForCustomers](#TemporaryInformationForCustomers)   | ?           | description               | See [temporaryInformationForCustomers](#TemporaryInformationForCustomers)                  |
| properties.callToAction                      | [callToAction](#CallToAction)                                           | ?           | public_url                | Deep links into SBB apps or external apps. See [callToAction](#CallToAction)          |
| properties.currentEstimatedOccupancy         | decimal                                                                 | ?           | has_realtime_data, realtime_free_capacity  | If not `null` or not `""`, then `has_realtime_data: true`. See [RealtimeParkingSites](#RealtimeParkingSites)  |
| properties.currentEstimatedOccupancyLevel         | [currentEstimatedOccupancyLevel](#CurrentEstimatedOccupancyLevel)                                                                 | ?           |          |   |



### ParkingFacilityCategory

| Key   | Mapping: purpose |
|-------|------------------|
| CAR   | CAR              |
| BIKE  | BIKE             |


### ParkingFacilityType

| Key                          | Mapping: park_and_ride_type | Mapping: type                                                          |
|------------------------------|-----------------------------|----------------------------------------------------------------------|
| PARK_AND_RAIL                | [ParkAndRideType.TRAIN]     | `OFF_STREET_PARKING_GROUND`|
| PARKING                      |                             | `OFF_STREET_PARKING_GROUND`|
| BIKE_PARKING                 |                             | If `properties.poiLevel` == 1 then `TWO_TIER` else `STANDS`           |
| BIKE_PARKING_COVERED         |                             | If `properties.poiLevel` == 1 then `TWO_TIER` else `SHED`               |
| BIKE_PARKING_SPACES          |                             | `FLOOR`                 |
| BIKE_PARKING_SPACES_COVERED  |                             | `SHED`               |
| BIKE_STATION                 |                             | if `properties.poiLevel` == 1 then `TWO_TIER` else `STANDS`               |


### Address

| Field       | Type   | Cardinality | Mapping | Comment   |
|-------------|--------|-------------|---------|-----------|
| addressLine | string | ?           | address |           |
| postalCode  | string | 1           | address |           |
| city        | string | 1           | address |           |


### Capacities

| Field        | Type                              | Cardinality | Mapping                           | Comment                          |
|--------------|-----------------------------------|-------------|-----------------------------------|----------------------------------|
| categoryType | [categoryType](#CategoryType)     | 1           | restrictions[].type               |                                  |
| total        | integer                           | 1           | capacity, restrictions[].capacity | `0` values should be ignored. The sum of all `capacities[].total > 0` entries is used as the site capacity.    |


### CategoryType

| Key                     | Mapping                                                          | Comment                                                                 |
|---------------------------|------------------------------------------------------------------|-------------------------------------------------------------------------|
| STANDARD                  | capacity                                                         | Summed together with other category types as sites capacity                |
| DISABLED_PARKING_SPACE    | capacity, restrictions[].type = `DISABLED`, restrictions[].capacity        | Summed together with other category types as sites capacity    |
| WITH_CHARGING_STATION     | capacity, restrictions[].type = `CHARGING`, restrictions[].capacity        | Summed together with other category types as sites capacity |
| RESERVABLE_PARKING_SPACE     | capacity        | Summed together with other category types as sites `capacity` |


### OperationTime

| Field         | Type                      | Cardinality | Mapping       | Comment                                                                                       |
|---------------|---------------------------|-------------|---------------|-----------------------------------------------------------------------------------------------|
| operatingFrom | string (`HH:MM:SS`)       | 1           | opening_hours |                                                                                               |
| operatingTo   | string (`HH:MM:SS`)       | 1           | opening_hours | `00:00:00` is rendered as `24:00` when it is the closing time.                                |
| daysOfWeek    | [daysOfWeek](#DaysOfWeek) | 1           | opening_hours |                                                                                               |


### DaysOfWeek

| Value     | Mapping       |
|-----------|---------------|
| MONDAY    | `Mo`          |
| TUESDAY   | `Tu`          |
| WEDNESDAY | `We`          |
| THURSDAY  | `Th`          |
| FRIDAY    | `Fr`          |
| SATURDAY  | `Sa`          |
| SUNDAY    | `Su`          |

Monday–Friday with the same time are collapsed to `Mo-Fr`; the weekend days are emitted separately. If all seven days
are present and both times are `00:00:00`, the result is `24/7`.


### AdditionalInformationForCustomers

| Field   | Type   | Cardinality | Mapping     | Comment                              |
|---------|--------|-------------|-------------|--------------------------------------|
| deText  | string | ?           | description | Used for `description`.              |
| enText  | string | ?           |             |                                      |
| frText  | string | ?           |             |                                      |
| itText  | string | ?           |             |                                      |


### SalesChannels

| Value              | Mapping         | Comment        |
|--------------------|-----------------|--------------- |
| P_RAIL_APP         |                 |                |
| ONLINE_AND_AUTOMAT |                 |                |
| ICT_PORTAL         |                 |                |
| PARKING_METER      |                 |                |
| E_CHARGING         |                 |                |


### PricingModel

| Field                                                        | Type                            | Cardinality | Mapping |
|--------------------------------------------------------------|---------------------------------|-------------|---------|
| minimumDuration                                              | integer                         | 1           |         |
| maximumDuration                                              | integer                         | 1           |         |
| maximumDayPrice                                              | integer                         | ?           |         |
| viableIncrement                                              | integer                         | 1           |         |
| priceSegments                                                | [priceSegments](#PriceSegments) | ?           |         |
| monthlyTicketPrice                                           | integer                         | ?           |         |
| yearlyTicketPrice                                            | integer                         | ?           |         |
| monthlyTicketPriceWithPublicTransportSeasonTicketDiscount    | integer                         | ?           |         |
| yearlyTicketPriceWithPublicTransportSeasonTicketDiscount     | integer                         | ?           |         |


### PriceSegments

| Field        | Type    | Cardinality | Mapping |
|--------------|---------|-------------|---------|
| startingFrom | integer | 1           |         |
| price        | integer | 1           |         |


### BikeFacilityTraits

| Field                           | Type   | Cardinality | Mapping     | Comment |
|---------------------------------|--------|-------------|-------------|---------|
| bikeFacilityTraitId             | string | 1           |             |         |
| bikeFacilityTraitNameI18n.de    | string | 1           | description |         |


### TemporaryInformationForCustomers

| Field  | Type   | Cardinality | Mapping      | Comment|
|--------|--------|-------------|--------------|--------|
| deText | string | 1           | description  |        |


### CallToAction

| Field              | Type   | Cardinality | Mapping    | Comment |
|--------------------|--------|-------------|------------|---------|
| sbbMobile.de       | string | ?           | public_url |         |
| externalMobile.de  | string | ?           | public_url |         |


### RealtimeParkingSites

| Field                                  | Mapping: realtime_free_capacity                                                                     | Comment                        |
|----------------------------------------|-----------------------------------------------------------------------------------------------------|--------------------------------|
| properties.currentEstimatedOccupancy   | round(capacities * (1.0 - currentEstimatedOccupancy)) | Where `capacities` is the sum of all `capacities[].total > 0` for `capacities[].categoryType` entries |


### CurrentEstimatedOccupancyLevel
| Value    | Mapping    | Comment           |
|----------|------------|-------------------|
| LOW      |            |                   |
| MEDIUM   |            |                   |
| HIGH     |            |                   |
