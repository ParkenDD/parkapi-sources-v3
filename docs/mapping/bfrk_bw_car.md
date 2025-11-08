# BFRK BW Car

BFRK BW Car is a large JSON dataset with static ParkingSite and ParkingSpot data.

* `purpose` is set to `CAR`
* `has_realtime_data` is set to `false`
* `name` is set to `Parkplatz`
* `static_data_updated_at` is set to now

If `stellplaetzegesamt` is more than 0, a `ParkingSite` is generated.

If `behindertenplaetze_lat`, `behindertenplaetze_lon` and `behindertenstellplaetze` are set and
`behindertenstellplaetze` is more than 0, one or more `ParkingSpot`s are generated, with
`restricted_to.type = 'DISABLED'`.

Multiple `ParkingSpot`s are distributed a bit from each other.


| Field                   | Type                        | Cardinality | Mapping `ParkingSite` | Mapping `ParkingSpot` | Comment                                                                |
|-------------------------|-----------------------------|-------------|-----------------------|-----------------------|------------------------------------------------------------------------|
| objektid                | integer                     | 1           | uid                   | uid                   |                                                                        |
| lat                     | numeric                     | 1           | lat                   |                       |                                                                        |
| lon                     | numeric                     | 1           | lon                   |                       |                                                                        |
| objekt_Foto             | string (url)                | ?           | photo_url             |                       |                                                                        |
| hst_dhid                | string                      | ?           | external_identifiers  | external_identifiers  |                                                                        |
| objekt_dhid             | string                      | ?           | external_identifiers  |                       |                                                                        |
| infraid                 | string                      | ?           |                       |                       |                                                                        |
| osmlinks                | string (url)                | ?           |                       |                       |                                                                        |
| gemeinde                | string                      | ?           | address               | address               |                                                                        |
| ortsteil                | string                      | ?           | address               | address               |                                                                        |
| art                     | [BfrkCarType](#BfrkCarType) | ?           | type                  | type                  | At `Park+Ride`, `park_and_ride_type` is set to `[ParkAndRideType.YES]` |
| stellplaetzegesamt      | integer                     | ?           | capacity              |                       |                                                                        |
| behindertenstellplaetze | integer                     | ?           | capacity_disabled     |                       |                                                                        |
| behindertenplaetze_lat  | numeric                     | ?           |                       | lat                   |                                                                        |
| behindertenplaetze_lon  | numeric                     | ?           |                       | lon                   |                                                                        |
| behindertenplaetze_Foto | string (url)                | ?           |                       | photo_url             |                                                                        |
| bedingungen             | string                      | ?           | description           |                       |                                                                        |
| eigentuemer             | string                      | ?           | operator_name         | operator_name         |                                                                        |


### BfrkCarType

| Key                      | Mapping                   |
|--------------------------|---------------------------|
| Park+Ride                | OFF_STREET_PARKING_GROUND |
| Kurzzeit                 | OFF_STREET_PARKING_GROUND |
| Parkhaus                 | CAR_PARK                  |
| Behindertenplätze        | OTHER                     |
| Parkplatz                | OFF_STREET_PARKING_GROUND |
| Parkplatz_ohne_Park+Ride | OFF_STREET_PARKING_GROUND |
