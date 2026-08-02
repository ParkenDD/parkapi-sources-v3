# Stadt Herrenberg

Stadt Herrenberg provides car parking data as JSON through the Stadtnavi ParkAPI endpoint.

* `purpose` is set to `CAR`
* `operator_name` is set to `Stadt Herrenberg`
* `static_data_updated_at` is set to `last_updated`
* `has_realtime_data` is set to `true`

A `ParkingSite` and `ParkingSpot` are generated for each valid entry in `lots`.
A `ParkingSpot` is generated only for disabled parking information if `total:disabled` is set and `== 1`
The `ParkingSpot` uses the same coordinates as its `ParkingSite` and obtains a `parking_site_id` to reference it.

Before validation, source keys containing `:` are normalized by replacing `:` with `_`, for example `total:disabled` becomes `total_disabled`.

## Static `ParkingSite`

| field                     | Type                    | Cardinality | Target field                      | Comment                                                                  |
| ------------------------- | ----------------------- | ----------- | --------------------------------- | ------------------------------------------------------------------------ |
| id                        | string                  | 1           | uid                               |                                                                          |
| name                      | string                  | 1           | name                              |                                                                          |
| lot_type                  | [LotType](#LotType)     | 1           | type, park_and_ride_type          |                                                                          |
| lots[].coords.lat         | numeric                 | 1           | lat                               |                                                                          |
| lots[].coords.lng         | numeric                 | 1           | lon                               |                                                                          |
| lots[].address            | string                  | 1           | address                           |                                                                          |
| lots[].total              | integer                 | 1           | capacity                          |                                                                          |
| lots[].total:disabled     | integer                 | ?           | restrictions[`DISABLED`].capacity | Set if present                                                           |
| lots[].notes.de           | string                  | ?           | description                       |                                                                          |
| lots[].url                | URL                     | ?           | public_url                        |                                                                          |
| lots[].opening_hours      | string                  | ?           | opening_hours                     | OSM opening times. `Mo - Su` is normalized to `Mo-Su`.                   |
| lots[].fee_hours          | string                  | ?           | has_fee                           | `has_fee` is set to `true` if `fee_hours` is present, otherwise `false`. |
| lots[].state              | [LotsState](#LotsState) | ?           | has_realtime_data                 | `false` if `state == nodata`, otherwise `true`.                          |
| last_updated              | datetime                | 1           | static_data_updated_at            | Converted to UTC.                                                        |

## Static `ParkingSpot`

| field                     | Type                    | Cardinality | Target field                      | Comment                                                                  |
| ------------------------- | ----------------------- | ----------- | --------------------------------- | ------------------------------------------------------------------------ |
| id                        | string                  | 1           | uid                               |                                                                          |
| name                      | string                  | 1           | name                              |                                                                          |
| lot_type                  | [LotType](#LotType)     | 1           | type, park_and_ride_type          |                                                                          |
| lots[].coords.lat         | numeric                 | 1           | lat                               |                                                                          |
| lots[].coords.lng         | numeric                 | 1           | lon                               |                                                                          |
| lots[].address            | string                  | 1           | address                           |                                                                          |
| lots[].total:disabled     | integer                 | ?           | restrictions[`DISABLED`].capacity | `ParkingSpot` is generated only when this value is exactly `1`.          |
| lots[].notes.de           | string                  | ?           | description                       |                                                                          |
| lots[].url                | URL                     | ?           | public_url                        |                                                                          |
| lots[].opening_hours      | string                  | ?           | opening_hours                     | OSM opening times. `Mo - Su` is normalized to `Mo-Su`.                   |
| lots[].fee_hours          | string                  | ?           | has_fee                           | `has_fee` is set to `true` if `fee_hours` is present, otherwise `false`. |
| lots[].state              | [LotsState](#LotsState) | ?           | has_realtime_data                 | `false` if `state == nodata`, otherwise `true`.                          |
| last_updated              | datetime                | 1           | static_data_updated_at            | Converted to UTC.                                                        |

## Realtime `ParkingSite`

Realtime `ParkingSite` data is generated for entries where `state != nodata`.

| field        | Type                    | Cardinality | Target field             | Comment                                               |
| ------------ | ----------------------- | ----------- | ------------------------ | ----------------------------------------------------- |
| lots[].id    | string                  | 1           | uid                      |                                                       |
| lots[].free  | integer                 | ?           | realtime_free_capacity   |                                                       |
| lots[].state | [LotsState](#LotsState) | ?           | realtime_opening_status  | Only `open`, `closed`, `many`, and `full` are mapped. |
| last_updated | datetime                | 1           | realtime_data_updated_at | Converted to UTC.                                     |

## LotType

| Key                      | Mapping: type             | Mapping: park_and_ride_type |
| ------------------------ | ------------------------- | --------------------------- |
| Parkplatz                | OFF_STREET_PARKING_GROUND |                             |
| Parkhaus                 | CAR_PARK                  |                             |
| Wohnmobilparkplatz       | OFF_STREET_PARKING_GROUND |                             |
| Park-Carpool             | OFF_STREET_PARKING_GROUND | [ParkAndRideType.CARPOOL]   |
| Park-Ride                | OFF_STREET_PARKING_GROUND | [ParkAndRideType.YES]       |
| Barrierefreier-Parkplatz | ON_STREET                 |                             |
| Tiefgarage               | UNDERGROUND               |                             |

## LotsState

| Key     | Mapping: realtime_opening_status |
| ------- | -------------------------------- |
| open    | OPEN                             |
| closed  | CLOSED                           |
| many    | OPEN                             |
| full    | OPEN                             |
| nodata  |                                  |
| unknown |                                  |