# BFRK BW Car

BFRK BW Car is a large JSON dataset with static ParkingSite and ParkingSpot data.

* `purpose` is set to `CAR`
* `has_realtime_data` is set to `false`
* `name` is set to `Parkplatz`
* `static_data_updated_at` is set to now

Usually, `ParkingSite`s are generated. If `behindertenstellplaetze_lat` and `behindertenstellplaetze_lon` are set,
additional `ParkingSpot` are generated, with `restricted_to.type = 'DISABLED'`.

Multiple `ParkingSpot`s are distributed a bit from each other.


| Field                       | Type                        | Cardinality | Mapping              | Comment                                                                |
|-----------------------------|-----------------------------|-------------|----------------------|------------------------------------------------------------------------|
| objektid                    | integer                     | 1           | uid                  |                                                                        |
| lat                         | numeric                     | 1           | lat                  |                                                                        |
| lon                         | numeric                     | 1           | lon                  |                                                                        |
| objekt_Foto                 | string (url)                | ?           | photo_url            |                                                                        |
| hst_dhid                    | string                      | ?           | external_identifiers |                                                                        |
| objekt_dhid                 | string                      | ?           | external_identifiers |                                                                        |
| infraid                     | string                      | ?           |                      |                                                                        |
| osmlinks                    | string (url)                | ?           |                      |                                                                        |
| gemeinde                    | string                      | ?           | address              |                                                                        |
| ortsteil                    | string                      | ?           | address              |                                                                        |
| art                         | [BfrkCarType](#BfrkCarType) | ?           | type                 | At `Park+Ride`, `park_and_ride_type` is set to `[ParkAndRideType.YES]` |
| stellplaetzegesamt          | integer                     | ?           | capacity             |                                                                        |
| behindertenstellplaetze     | integer                     | ?           | capacity_disabled    |                                                                        |
| behindertenstellplaetze_lat | numeric                     | ?           |                      | If set, create `ParkingSpot`s                                          |
| behindertenstellplaetze_lon | numeric                     | ?           |                      | If set, create `ParkingSpot`s                                          |
| bedingungen                 | string                      | ?           | description          |                                                                        |
| eigentuemer                 | string                      | ?           | operator_name        |                                                                        |


### BfrkCarType

| Key                      | Mapping                   |
|--------------------------|---------------------------|
| Park+Ride                | OFF_STREET_PARKING_GROUND |
| Kurzzeit                 | OFF_STREET_PARKING_GROUND |
| Parkhaus                 | CAR_PARK                  |
| Behindertenplätze        | OTHER                     |
| Parkplatz                | OFF_STREET_PARKING_GROUND |
| Parkplatz_ohne_Park+Ride | OFF_STREET_PARKING_GROUND |
