# Sensade Carpooling Static and Dynamic data

Sensade has provided Parking sites and Parking spots as Off-street parking lots () and parking spaces. 
In these parking lots, there are parking spaces which are mapped into single parking spots using their corresponding ids and coordinates.

The parking lots have both realtime and static data, while the parking spaces only have static data.


## `ParkingSite` Properties

Static values:

Each parking lot endpoint is mapped to static `ParkingSite` as follows.

Attributes which are set statically:
* `has_realtime_data` is set to `true`
* `purpose` is set to `CAR`
* `park_and_ride_type` is set to `YES`
* `type` is set to `OFF_STREET_PARKING_GROUND`


| Field                         | Type                                         | Cardinality | Mapping                                   | Comment                                                                            |
|-------------------------------|----------------------------------------------|-------------|-------------------------------------------|------------------------------------------------------------------------------------|
| id                            | string                                       | 1           | uid                                       |                                                                                    |
| name                          | string                                       | 1           | name                                      |                                                                                    |
| city                          | string                                       | 1           | address                                   |                                                                                    |
| address                       | string                                       | 1           | address                                   |                                                                                    |
| zip                           | integer                                      | 1           | address                                   |                                                                                    |
| availableSpaces               | integer                                      | 1           | capacity                                  |                                                                                    |
| creationDate                  | datetime                                     | 1           | static_data_updated_at                    |                                                                                    |
| latitude                      | string                                       | 1           | lat                                       |                                                                                    |
| longitude                     | string                                       | 1           | lon                                       |                                                                                    |
| parkingSpaces                 | [ParkingSpot](#ParkingSpot)                  | ?           | [ParkingSpot](#ParkingSpot)               |                                                                                    |


Realtime values:

Each parking lot status endpoint mapped to realtime `ParkingSite` as follows.

Attributes which are set statically:
* `has_realtime_data` is always `True`
* `realtime_data_updated_at` is set to the moment of import

| Field                         | Type                                         | Cardinality | Mapping                                   | Comment                                                                            |
|-------------------------------|----------------------------------------------|-------------|-------------------------------------------|------------------------------------------------------------------------------------|
| parkingLotId                  | string                                       | 1           | uid                                       |                                                                                    |
| totalSpaceCount               | integer                                      | ?           | realtime_capacity                         |                                                                                    |
| availableSpaceCount           | integer                                      | ?           | realtime_free_capacity                    |                                                                                    |


## `ParkingSpot` Properties

Static values:

Each parking space in a parking lot endpoint is mapped to static `ParkingSpot` as follows.

Attributes which are set statically or inherited:
* `has_realtime_data` is set to `false`
* `name` is inherited from `name` in `ParkingSite`
* `purpose` is inherited from `purpose` in `ParkingSite`
* `address` is inherited from `address` in `ParkingSite`
* `type` is inherited from `type` in `ParkingSite`
* `static_data_updated_at` is inherited from `static_data_updated_at` in `ParkingSite`

| Field                         | Type                                                | Cardinality | Mapping                            | Comment                                                                            |
|-------------------------------|-----------------------------------------------------|-------------|------------------------------------|------------------------------------------------------------------------------------|
| id                            | string                                              | 1           | uid                                |                                                                                    |
| latitude                      | string                                              | 1           | lat                                |                                                                                    |
| longitude                     | string                                              | 1           | lon                                |                                                                                    |
