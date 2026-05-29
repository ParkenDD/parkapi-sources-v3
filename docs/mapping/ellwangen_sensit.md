# Ellwangen Parking Lots via Sensit API

Ellwangen provides JSON realtime parking lots data via a secured Sensit REST-API Endpoint `/api/v1/parkingLots`. The feed contains one parking object with static
location and capacity fields together with realtime occupancy information.

Attributes which are set statically:

* `type` is always set to `OFF_STREET_PARKING_GROUND`
* `purpose` is always set to `CAR`
* `has_realtime_data` is always set to `true`
* `realtime_data_updated_at` not provided, to be set in the converter

## ParkingSite

Each object in the JSON array is mapped to a `ParkingSite` as follows.

| Field              | Type                                | Cardinality | Mapping     | Comment                                              |
|--------------------|-------------------------------------|-------------|-------------|------------------------------------------------------|
| id                 | string                              | 1           | uid         |                                                      |
| name               | string                              | 1           | name        |                                                      |
| actualStatus       | [ActualStatus](#ActualStatus)       | 1           |             | Contains realtime capacity and occupancy values      |
| location           | [Location](#Location)               | 1           |             | Contains geometric information e.g. coordinates      |


## ActualStatus

| Field           | Type    | Cardinality | Mapping                       | Comment                                                       |
|-----------------|---------|-------------|-------------------------------|---------------------------------------------------------------|
| parkingCapacity | integer | 1           | capacity/realtime_capacity    |                                                               |
| vacantSpaces    | integer | 1           | realtime_free_capacity        | Presence of this field indicates realtime data is available   |


## Location

| Field     | Type    | Cardinality | Mapping | Comment               |
|-----------|---------|-------------|---------|-----------------------|
| latitude  | decimal | 1           | lat     | Transform to string |
| longitude | decimal | 1           | lon     | Transform to string | 
