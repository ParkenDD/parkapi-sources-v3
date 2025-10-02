# Sensade Carpooling Static and Dynamic data

Sensade has provided Parking sites and Parking spots for Off-street parking lots and parking spaces. 
In these parking lots, there are parking spaces which are mapped into single parking spots using their corresponding ids and coordinates.

The parking lots have both realtime and static data, while the parking spaces only have static data.


## `ParkingSite` Properties

Each parking lot is mapped to static `ParkingSite` as follows.

Attributes which are set statically:
* `has_realtime_data` is set to `true`
* `purpose` is set to `CAR`
* `park_and_ride_type` is set to `YES`


| Field                         | Type                                         | Cardinality | Mapping                                 | Comment                                                                            |
|-------------------------------|----------------------------------------------|-------------|-----------------------------------------|------------------------------------------------------------------------------------|
| id                            | string                                       | 1           | uid                                     |                                                                                    |
| maxcarparkfull                | integer                                      | ?           | realtime_capacity                       |                                                                                    |
| currentcarparkfulltotal       | integer                                      | ?           | realtime_free_capacity                  |                                                                                    |
| timestamp                     | datetime                                     | 1           | realtime_data_updated_at                |                                                                                    |

## `ParkingSpot` Properties

Each parking space is mapped to `ParkingSpot` as follows.

| Field           | Type                                                | Cardinality | Mapping                                         | Comment                                                                            |
|-----------------|-----------------------------------------------------|-------------|-------------------------------------------------|------------------------------------------------------------------------------------|
| id              | string                                              | 1           | uid                                             |                                                                                    |
| occupied        | [ParkingSpotStatus](#ParkingSpotStatus)             | 1           | realtime_status                                 |                                                                                    |
| timestamp       | datetime                                            | 1           | realtime_data_updated_at                        |                                                                                    |

### ParkingSpotStatus

| Key         | Mapping       |
|-------------|---------------|
| True        | TAKEN         |
| False       | AVAILABLE     |