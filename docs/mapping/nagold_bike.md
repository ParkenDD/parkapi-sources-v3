# Nagold Bike Parking

The city of Nagold publishes a GeoJSON dataset with locations of bicycle parking installations across the city. Each feature describes a group of bicycle stands or racks available for public use.


## `ParkingSite` Properties

Static values:

Each bicycle parking installation is mapped to a static `ParkingSite` as follows.
Parking installations with `"Stellplatz": " "` and `"Anzahl_Bue": 0` should not be integrated.

Attributes which are set statically by the converter:

* `has_realtime_data` is always set to `false`
* `opening_hours` is set to `24/7` when `Immer_geoe` is `ja`
* `purpose` is always set to `BIKE`
* `lat` and `lon` are set from the standard GeoJSON coordinates point, 

| Field                 | Type                              | Cardinality | Mapping                                           | Comment                                                             |
|-----------------------|-----------------------------------|-------------|---------------------------------------------------|---------------------------------------------------------------------|
| OBJECTID              | string                            | 1           | uid                                               |                                                                     |
| Strasse               | string                            | 1           | name                                              | Street name used as parking facility name                           |
| Lagebeschr            | string                            | ?           | description                                       | Parking description (e.g. "Am Parkplatz vom Polizeirevier")         |
| coordinates[1]        | numeric                           | 1           | lat                                               | GeoJSON geometry coordinates index 1                                |
| coordinates[0]        | numeric                           | 1           | lon                                               | GeoJSON geometry coordinates index 0                                |
| Stellplatz            | [Stellplatz](#Stellplatz)         | 1           | type                                              | See [Stellplatz](#Stellplatz)                                       |
| Anzahl_Bue            | integer                           | 1           | capacity                                          |                                                                     |
| Anzahl_Lad            | integer                           | 1           | [restrictions](#ParkingSiteRestriction)           | Map to `CHARGING` restrictions if > 0                               |
| Beleuchtun            | [Beleuchtung](#Beleuchtung)       | 1           | has_lighting                                      | See [Beleuchtung](#Beleuchtung)                                     |
| Ueberdachu            | [Ueberdachung](#Ueberdachung)     | 1           | is_covered                                        | See [Ueberdachung](#Ueberdachung)                                   |
| Bike_and_R            | [Bike_and_Ride](#ParkAndRideType) | 1           | park_and_ride_type                                | See [Bike_and_Ride](#ParkAndRideType)                                 |
| Ueberwachu            | [Ueberwachung](#Ueberwachung)     | 1           | supervision_type                                  | See [Ueberwachung](#Ueberwachung)                                   |
| Betreiber             | string                            | ?           | operator_name                                     | Omit if blank                                                       |
| last_edi_1            | integer                           | 1           | static_data_updated_at                            | Convert epoch milliseconds to ISO 8601                              |


## Beleuchtung

| Key  | Mapping |
|------|---------|
| ja   | `True`  |
| nein | `False` |


## Ueberdachung

| Key  | Mapping |
|------|---------|
| ja   | `True`  |
| nein | `False` |


## Stellplatz

| Key                  | Mapping      |
|----------------------|--------------|
| Anlehnbügel          | `STANDS`     |
| Vorderradanschluss   | `WALL_LOOPS` |


## ParkAndRideType

| Key  | Mapping    |
|------|------------|
| ja   | `["YES"]`  |
| nein | `["NO"]`   |


## ParkingSiteRestriction

| Key        | Mapping                    |
|------------|----------------------------|
| Anzahl_Lad | `ParkingAudience.CHARGING` |


## Ueberwachung

| Key  | Mapping |
|------|---------|
| ja   | `YES`   |
| nein | `NO`    |


