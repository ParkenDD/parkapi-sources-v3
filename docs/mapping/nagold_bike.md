# Nagold Bike Parking

The city of Nagold publishes a GeoJSON dataset with locations of bicycle parking installations across the city. Each feature describes a group of bicycle stands or racks available for public use.


## `ParkingSite` Properties

Static values:

Each bicycle parking installation is mapped to a static `ParkingSite` as follows.
Parking installations with `"Stellplatzart": " "` and `"Anzahl_Buegel_Stellplaetze": 0` should not be integrated.

Attributes which are set statically by the converter:

* `has_realtime_data` is always set to `false`
* `opening_hours` is set to `24/7` when `Immer_geoeffnet_zugaenglich` is `ja`
* `purpose` is always set to `BIKE`
* `lat` and `lon` are set from the standard GeoJSON coordinates point

| Field                      | Type                                | Cardinality | Mapping                                  | Comment                                                     |
|----------------------------|-------------------------------------|-------------|------------------------------------------|-------------------------------------------------------------|
| OBJECTID                   | string                              | 1           | uid                                      |                                                             |
| Strasse                    | string                              | 1           | name                                     | Street name used as parking facility name                   |
| Lagebeschreibung           | string                              | ?           | description                              | Parking description (e.g. "Am Parkplatz vom Polizeirevier") |
| coordinates[1]             | numeric                             | 1           | lat                                      | GeoJSON geometry coordinates index 1                        |
| coordinates[0]             | numeric                             | 1           | lon                                      | GeoJSON geometry coordinates index 0                        |
| Stellplatzart              | [Stellplatzart](#Stellplatzart)     | 1           | type                                     | See [Stellplatzart](#Stellplatzart)                         |
| Anzahl_Buegel_Stellplaetze | integer                             | 1           | capacity                                 |                                                             |
| Anzahl_Lademoeglichkeiten  | integer                             | 1           | [restrictions](#ParkingSiteRestriction)  | Map to `CHARGING` restrictions if > 0                       |
| Beleuchtung                | [Beleuchtung](#Beleuchtung)         | 1           | has_lighting                             | See [Beleuchtung](#Beleuchtung)                             |
| Ueberdachung               | [Ueberdachung](#Ueberdachung)       | 1           | is_covered                               | See [Ueberdachung](#Ueberdachung)                           |
| Bike_and_Ride              | [ParkAndRideType](#ParkAndRideType) | 1           | park_and_ride_type                       | See [ParkAndRideType](#ParkAndRideType)                     |
| Ueberwachung               | [Ueberwachung](#Ueberwachung)       | 1           | supervision_type                         | See [Ueberwachung](#Ueberwachung)                           |
| Betreiber                  | string                              | ?           | operator_name                            | Omit if blank                                               |
| last_edited_date           | integer                             | 1           | static_data_updated_at                   | Convert epoch milliseconds to ISO 8601                      |


## Beleuchtung

| Key   | Mapping |
|-------|---------|
| ja    | `True`  |
| nein  | `False` |


## Ueberdachung

| Key  | Mapping |
|------|---------|
| ja   | `True`  |
| nein | `False` |


## Stellplatzart

| Key                                    | Mapping           |
|----------------------------------------|-------------------|
| Anlehnbügel                            | `STANDS`          |
| Vorderradanschluss                     | `WALL_LOOPS`      |
| Vorderradhalter mit Rahmen-Sicherung   | `SAFE_WALL_LOOPS` |


## ParkAndRideType

| Key   | Mapping    |
|-------|------------|
| ja    | `["YES"]`  |
| nein  | `["NO"]`   |


## ParkingSiteRestriction

| Key                       | Mapping                    |
|---------------------------|----------------------------|
| Anzahl_Lademoeglichkeiten | `ParkingAudience.CHARGING` |


## Ueberwachung

| Key  | Mapping |
|------|---------|
| ja   | `YES`   |
| nein | `NO`    |

