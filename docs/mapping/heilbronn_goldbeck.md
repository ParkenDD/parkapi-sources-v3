# Stadtwerke Heilbronn - Goldbeck Parking Services

Stadtwerke Heilbronn provides parking facility details and realtime occupancies via the GOLDBECK Parking Services API. 
The converter merges both parking places by facility id and only processes active facilities that expose capacity data in realtime counters.

* `purpose` is always `CAR`
* `type` is always `CAR_PARK`
* `has_realtime_data` is always `True`

Static values:

* `capacity` comes from the occupancies counters with type `TOTAL` and counters with reservation status `UNKNOWN` and `NO_RESERVATIONS`.
* Only the first active tariff is considered for `has_fee`.

Static data are pulled from the `occupancies` and `facilities` API endpoints. 

| Source field/path            | Type        | Cardinality | Target field              | Comment                                                                                                  |
|------------------------------|-------------|-------------|---------------------------|----------------------------------------------------------------------------------------------------------|
| id                           | integer     | 1           | uid                       |                                                                                                          |
| name                         | string      | 1           | name                      |                                                                                                          |
| position.latitude            | number      | 1           | lat                       |                                                                                                          |
| position.longitude`          | number      | 1           | lon                       |                                                                                                          |
| postalAddress.street1        | string      | ?           | address                   | Combined as `<street1> <street2>, <zip> <city>` when available                                         |
| postalAddress.street2        | string      | ?           | address                   | Combined as `<street1> <street2>, <zip> <city>` when available                                         |
| postalAddress.zip            | string      | ?           | address                   | Combined as `<street1> <street2>, <zip> <city>` when available                                         |
| postalAddress.city           | string      | ?           | address                   | Combined as `<street1> <street2>, <zip> <city>` when available                                         |
| counters                     | list        | ?           | [Counters](#Counters)     | when `type` is `TOTAL` and `reservationStatus` is `UNKNOWN` or `reservationStatus` is `NO_RESERVATIONS`  |
| tariffs                      | list        | ?           | [Tariffs](#Tariffs)       |                                                                                                          |
| lastUpdatedAt                | datetime    | 1           | static_data_updated_at    |                                                                                                          |

Realtime values:

* Only facilities marked `active` in static data are emitted
* Requires a realtime counter when `type` is `TOTAL` and `reservationStatus` is `UNKNOWN` or `reservationStatus` is `NO_RESERVATIONS`; otherwise the site is skipped with a warning

| Source field/path           | Type        | Cardinality | Target field              | Comment                                                                                                  |
|-----------------------------|-------------|-------------|---------------------------|----------------------------------------------------------------------------------------------------------|
| facilityId                  | integer     | 1           | uid                       |                                                                                                          |
| counters                    | list        | ?           | [Counters](#Counters)     | when `type` is `TOTAL` and `reservationStatus` is `UNKNOWN` or `reservationStatus` is `NO_RESERVATIONS`  |
| valuesFrom                  | datetime    | 1           | realtime_data_updated_at  |                                                                                    |


## Counters

| Source field/path           | Type        | Cardinality | Target field                   | Comment                                                                            |
|-----------------------------|-------------|-------------|--------------------------------|------------------------------------------------------------------------------------|
| maxPlaces                   | integer     | ?           | capacity/realtime_capacity     |                                                                                    |
| occupiedPlaces              | integer     | ?           | realtime_free_capacity         | Subtract  `occupiedPlaces` from `maxPlaces` if `freePlaces` is -1 or less than 0   |
| freePlaces                  | integer     | ?           | realtime_free_capacity         |                                                                                    |


## Tariffs

| Source field/path           | Type       | Cardinality | Target field                  | Comment                                                                                                  |
|-----------------------------|------------|-------------|-------------------------------|----------------------------------------------------------------------------------------------------------|
| isActive                    | boolean    | ?           | has_fee                       | Set to `has_fee` when any tariff is provided, returns `False` when `isActive` is missing or `false`      |
| tariffItems                 | list       | ?           | [TariffItems](#TariffItems)   | When `isActive` is `true` and any tariff item is provided                                                |


## TariffItems

| Source field/path           | Type        | Cardinality | Target field              | Comment                                                                                     |
|-----------------------------|-------------|-------------|---------------------------|---------------------------------------------------------------------------------------------|
| plainTextValue              | string      | ?           | fee_description           | Only used when the string is validated as `safe`, returns `None` when string `unsafe`       |