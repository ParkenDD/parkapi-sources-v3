# Nagold Bike Parking

The city of Nagold publishes a GeoJSON dataset with locations of bicycle parking installations across the city. Each feature describes a group of bicycle stands or racks available for public use.


## `ParkingSite` Properties

Static values:

Each bicycle parking installation is mapped to a static `ParkingSite` as follows.
Attributes which are set statically by the converter:

* `has_realtime_data` is always set to `False`
* `opening_hours` is set to `24/7` when `Immer_geoe` is `ja`

| Field                 | Type                              | Cardinality | Mapping                                           | Comment                                                             |
|-----------------------|-----------------------------------|-------------|---------------------------------------------------|---------------------------------------------------------------------|
| OBJECTID              | string                            | 1           | uid                                               |                                                                     |
| Strasse               | string                            | 1           | name                                              | Street name used as primary name                                    |
| Lagebeschr            | string                            | ?           | description                                       | Location description (e.g. "Am Parkplatz vom Polizeirevier")        |
| coordinates[1]        | numeric                           | 1           | lat                                               | GeoJSON geometry coordinates index 1                                |
| coordinates[0]        | numeric                           | 1           | lon                                               | GeoJSON geometry coordinates index 0                                |
| Stellplatz            | [Stellplatz](#Stellplatz)         | ?           | type                                              | See [Stellplatz](#Stellplatz)                                       |
| Anzahl_Bue            | integer                           | 1           | capacity                                          |                                                                     |
| Anzahl_Lad            | integer                           | ?           | [restrictions](#ParkingSiteRestriction)           | Map to `CHARGING` restrictions if > 0                               |
| Beleuchtun            | [Beleuchtung](#Beleuchtung)       | ?           | has_lighting                                      |                                                                     |
| Ueberdachu            | [Ueberdachung](#Ueberdachung)     | ?           | is_covered                                        |                                                                     |
| Bike_and_R            | [Bike_and_Ride](#Bike_and_Ride)   | ?           | park_and_ride_type                                | See [Bike_and_Ride](#Bike_and_Ride)                                 |
| Ueberwachu            | [Ueberwachung](#Ueberwachung)     | ?           | supervision_type                                  |                                                                     |
| Betreiber             | string                            | ?           | operator_name                                     | Omit if blank                                                       |
| last_edi_1            | epoch ms                          | ?           | static_data_updated_at                            | Convert epoch milliseconds to ISO 8601                              |
| created_da            | epoch ms                          | ?           | static_data_updated_at                            | Fallback if `last_edi_1` is not available                           |


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
| None                 | `STANDS`     |


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


