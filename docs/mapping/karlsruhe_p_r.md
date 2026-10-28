# TechnologieRegion Karlsruhe: Park and Ride

The TechnologieRegion Karlsruhe publishes its Park and Ride sites as GeoJSON with Point geometries at the layer
`TBA:park_ride` of its [GeoServer](https://mobil.trk.de/geoserver/TBA/ows). The layer is published at the Mobilithek by
Digitale Mobilität ([offer](https://mobilithek.info/offers/-473937279490085166)). Each feature becomes a `ParkingSite`.
Static and realtime data are taken from the same layer.

Features without `stellplaetze` or with `stellplaetze` `0` are ignored. If the config key
`PARK_API_KARLSRUHE_P_R_IGNORE_MISSING_CAPACITIES` is set to `false`, features without `stellplaetze` are reported as
validation errors instead, and features with `0` are imported.

Static values:

* `purpose` is always `CAR`
* `type` is always `OTHER`
* `park_and_ride_type` is always `[YES]`
* `lat` / `lon` are taken from the Point geometry, rounded to 7 decimal places
* text fields have non-breaking spaces replaced by spaces, line breaks by spaces and carriage returns removed

## Static data

| Field                    | Type               | Cardinality | Mapping                | Comment                                                                     |
|--------------------------|--------------------|-------------|------------------------|-----------------------------------------------------------------------------|
| id                       | integer            | 1           | uid                    |                                                                             |
| gemeinde                 | string             | 1           | name, address          | `name` is `{gemeinde}: {haltestelle}`                                       |
| stadtteil                | string             | ?           | address                | `address` is `{stadtteil}, {gemeinde}`; just `{gemeinde}` if both are equal |
| haltestelle              | string             | 1           | name                   |                                                                             |
| stellplaetze             | integer            | ?           | capacity               | ignored per default if missing or `0`                                       |
| bemerkung                | string             | ?           | description            |                                                                             |
| freie_parkplaetze        | integer            | ?           |                        | see realtime data                                                           |
| freie_parkplaetze_anteil | numeric            | ?           |                        | share of free spaces                                                        |
| echtzeit_status          | string             | ?           |                        | always `OK` if present                                                      |
| echtzeit_belegung        | string             | 1           | has_realtime_data      | `T` or `F`                                                                  |
| p_r_id                   | string             | ?           |                        | e.g. `BADEN_10`                                                             |
| stand_freieparkplaetze   | string (date-time) | ?           |                        | see realtime data                                                           |
| stand_stammdaten         | string (date-time) | ?           | static_data_updated_at | import time if missing                                                      |

## Realtime data

Realtime data is only created for features with `echtzeit_belegung` `T` and a `stand_freieparkplaetze`.

| Field                  | Type               | Cardinality | Mapping                  | Comment |
|------------------------|--------------------|-------------|--------------------------|---------|
| id                     | integer            | 1           | uid                      |         |
| stellplaetze           | integer            | 1           | realtime_capacity        |         |
| freie_parkplaetze      | integer            | ?           | realtime_free_capacity   |         |
| stand_freieparkplaetze | string (date-time) | 1           | realtime_data_updated_at |         |
