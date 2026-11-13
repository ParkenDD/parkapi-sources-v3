# Contipark

Contipark provides a JSON REST API (`/v1/carparks`) with static parking site data across Germany. Access
requires a certificate (`PARK_API_CONTIPARK_CERT_PATH`). The response contains a `data` list, where
each entry is one parking site. The API models only static data.

As car parks in the API have only the coordinates and addresses of the gates and not from the car park itself, the first gate is used for address and coordinates of the hole car_aprk, as there needs to be at least one gate.

Static values:

* `has_realtime_data` is always `False` (the API does not offer realtime data yet)
* `purpose` is always `CAR`

## Properties

| Field                                           | Type                                      | Cardinality | Mapping                | Comment                                                       |
|-------------------------------------------------|-------------------------------------------|-------------|------------------------|---------------------------------------------------------------|
| publicID["value"]                               | string                                    | 1           | original_uid           |                                                               |
| consumerManagement["mcpUrl"]["value"]           | string (url)                              | ?           | public_url             |                                                               |
| gates[0]["street"]["value"]                     | str                                       | 1           | address                |                                                               |
| gates[0]["houseNumber"]["value"]                | str                                       | 1           | address                |                                                               |
| gates[0]["zipCode"]["value"]                    | str                                       | 1           | address                |                                                               |
| consumerManagement["mcpDescriptionDE"]["value"] | str                                       | description |                        |                                                               |
| type["value"]                                   | [ParkingSiteType](#parkingsitetype)       | 1           | type                   |                                                               |
| type["value"]                                   | [is_covered](#is_covered)                 | 1           | is_covered             |                                                               |
| namePublicDE["value"]                           | string                                    | 1           | name                   |                                                               |
| namePublicEN["value"]                           | string                                    |             |                        |                                                               |
| dimensions["height"]["value"]                   | Number                                    | 1           | max_height             |                                                               |
| dimensions["width"]["value"]                    | Number                                    | 1           | max_width              |                                                               |
| bahnPark["isBahnPark"]                          | [ParkAndRideType](#parkandridetype)       | 1           | park_and_ride_type     |                                                               |
| tags["locations"]["value"]                      | string                                    | ?           | related_location       |                                                               |
| openingHours                                    | object                                    | 1           | opening_hours          | requires custom conversion logic based on the provided format |
| parkingSpots["total"]["value"]                  | int                                       | 1           | capacity               |                                                               |
| tags                                            | object                                    | 1           | tags                   |                                                               |
| gates[0]["lat"]["value"]                        | Number                                    | 1           | lat                    |                                                               |
| gates[0]["lon"]["value"]                        |                                           | 1           | lon                    |                                                               |
| parkingspots                                    | [ParkingRestriction](#parkingrestriction) | 1           | restrictions           |                                                               |
| static_data_updated_at                          | str(date-time)                            | 1           | static_data_updated_at |                                                               |

### ParkingSiteType

| Key | Mapping: type             |
|-----|---------------------------|
| PD  | CAR_PARK                  |
| PH  | CAR_PARK                  |
| PP  | OFF_STREET_PARKING_GROUND |
| TG  | UNDERGROUND               |

### is_covered

| Key | Mapping: is_covered       |
|-----|---------------------------|
| PD  | false                     |
| PH  | true                      |
| PP  | false                     |
| TG  | true                      |

### parkandridetype

| Key | Mapping: park_and_ride_type |
|-----|-----------------------------|
| true| TRAIN                       |

### ParkingRestriction

| Key          | Mapping: restrictions.type   |
|--------------|------------------------------|
| women        | WOMEN                        |
| disabled     | DISABLED                     |
| motorhome    | CARAVAN                      |
| xxl          |                              |
| bahnComfort  |                              |
| mini         |                              |
| bus          | BUS                          |
| motorcycle   |                              |
| shortTerm    |                              |
| bicycle      |                              |
| pcardService |                              |
| motherChild  | FAMILY                       |
| truck        | TRUCK                        |
| senior       |                              |
