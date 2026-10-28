# TechnologieRegion Karlsruhe: Parken und Mitfahren

The TechnologieRegion Karlsruhe publishes its car pool parking sites (Parken und Mitfahren) as GeoJSON with Point
geometries at the layer `TBA:parken_mitfahren` of its [GeoServer](https://mobil.trk.de/geoserver/TBA/ows). The layer is
published at the Mobilithek by Digitale Mobilität ([offer](https://mobilithek.info/offers/-5814095015232635690)). Each
feature becomes a `ParkingSite`. There is no realtime data.

Features without `stellplaetze` or with `stellplaetze` `0` are ignored. If the config key
`PARK_API_KARLSRUHE_P_M_IGNORE_MISSING_CAPACITIES` is set to `false`, features without `stellplaetze` are reported as
validation errors instead, and features with `0` are imported.

Static values:

* `purpose` is always `CAR`
* `type` is always `OFF_STREET_PARKING_GROUND`
* `park_and_ride_type` is always `[CARPOOL]`
* `has_realtime_data` is always `false`
* `lat` / `lon` are taken from the Point geometry, rounded to 7 decimal places
* text fields have non-breaking spaces replaced by spaces, line breaks by spaces and carriage returns removed

## Static data

| Field                | Type               | Cardinality | Mapping                | Comment                                                 |
|----------------------|--------------------|-------------|------------------------|---------------------------------------------------------|
| id                   | integer            | 1           | uid                    |                                                         |
| standort             | string             | 1           | name                   |                                                         |
| strasse              | string             | ?           | address                | e.g. `D 919` or `Rheinbrückenstraße`                    |
| stellplaetze         | integer            | 1           | capacity               | ignored per default if missing or `0`                   |
| anschlussstelle_nr   | string             | ?           |                        | number of the nearby motorway junction                  |
| anschlussstelle_name | string             | ?           |                        | name of the nearby motorway junction                    |
| bemerkung            | string             | ?           | description            |                                                         |
| stand                | string (date-time) | 1           | static_data_updated_at |                                                         |
