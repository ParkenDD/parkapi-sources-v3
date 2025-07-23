# Realtime and Static P+R data of the city of Freiburg

The city of Freiburg provides realtime ``GEOJSON`` parking data for static and realtime Park + Ride for cars.

##  P+R-Static ParkingSites

Attributes which are set statically:
* `has_realtime_data` is always set to `False`

A `ParkingSites` provides static data for a Park and Ride `ParkingSite`.

| Field                      | Type                     | Cardinality | Mapping                         | Comment                                                             |
|----------------------------|--------------------------|-------------|---------------------------------|---------------------------------------------------------------------|
| ogc_fid                    | integer                  | 1           | uid                             |                                                                     |
| kapazitaet                 | integer                  | 1           | capacity                        |                                                                     |
| name                       | string                   | 1           | name                            |                                                                     |
| nummer                     | string                   | 1           | name                            | Empty strings will be ignored                                       |
| kategorie                  | string                   | 1           | [type](#ParkingSiteType)        |                                                                     |


## P+R-Realtime and Static ParkingSites 

Attributes which are set statically:
* `type` is always set to `OFF_STREET_PARKING_GROUND`
* `park_and_ride_type` is always set to `['YES']`
* `purpose` is always set to `CAR`
* `has_realtime_data` is always set to `True`

A `ParkingSites` provides static and realtime data for a Park and Ride `ParkingSite`.

| Field                      | Type                     | Cardinality | Mapping                                            | Comment                                                             |
|----------------------------|--------------------------|-------------|----------------------------------------------------|---------------------------------------------------------------------|
| park_id                    | integer                  | 1           | uid                                                |                                                                     |
| name                       | string                   | 1           | name                                               |                                                                     |
| obs_max                    | integer                  | 1           | realtime_capacity/capacity                         |                                                                     |
| obs_free                   | integer                  | 1           | realtime_free_capacity                             |                                                                     |
| obs_ts                     | datetime                 | 1           | realtime_data_updated_at                           |                                                                     |
| obs_state                  | integer                  | 1           | [realtime_opening_status](#RealtimeOpeningStatus)  |                                                                     |

#### RealtimeOpeningStatus

| Key        | Mapping        | Comment                                                         |
|------------|----------------|-----------------------------------------------------------------|
| 0          | OPEN           | Free parking spaces (Normalbetrieb, Freie Plätze verfügbar)     |
| 1          | OPEN           | Less than 30 parking spaces (Weniger als 30 Restplätze)         |
| 2          | OPEN           | Less than 10 parking spaces (Weniger als 10 Restplätze)         |
| -1         | CLOSED         | No data (Störung / Keine Daten)                                 |

#### ParkingSiteType

| Key           | Mapping                        |
|---------------|--------------------------------|
| Parkplatz     | OFF_STREET_PARKING_GROUND      |
| Parkhaus      | CAR_PARK                       |
| Tiefgarage    | UNDERGROUND                    |
| Park&Ride     | OFF_STREET_PARKING_GROUND      |
| None          | OTHER                          |