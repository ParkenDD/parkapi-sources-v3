# RadVIS BW Bike Parking

The state of Baden-Württemberg publishes a GeoJSON dataset with locations of bicycle parking facilities.
Each feature describes a group of bicycle stands or racks available for public use.

The geometry coordinates are in a projected CRS (UTM zone 32N, WGS84 ellipsoid, EPSG:25832). The converter reprojects them to WGS84 lat/lon using `pyproj` before creating the `ParkingSite`.

Parking facilities with `"status": "GEPLANT"` (planned) or `"status": "AUSSER_BETRIEB"` (not in operation) should not be integrated.
Parking sites with `"quell_system": "MOBIDATABW"` (as source system) should not be integrated either, because RadVIS contains duplicated data from the MobiDataBW.


## `ParkingSite` Properties

Static values:

Each bicycle parking installation is mapped to a static `ParkingSite` as follows.

Attributes which are set statically by the converter:

* `has_realtime_data` is always set to `false`
* `purpose` is always set to `BIKE`, except for `"stellplatzart": "SCHLIESSFACH"` which is mapped to `ITEM` (see [Stellplatzart](#Stellplatzart))
* `lat` and `lon` are computed from the GeoJSON point geometry, reprojected from UTM zone 32N (EPSG:25832) to WGS84
* `uid` is derived from the numeric feature id

| Field                          | Type                                     | Cardinality | Mapping                                           | Comment                                                                                         |
|--------------------------------|------------------------------------------|-------------|---------------------------------------------------|-------------------------------------------------------------------------------------------------|
| id                             | integer                                  | 1           | uid                                               |                                                                                                 |
| name                           | string                                   | ?           | name                                              | Fallback to `Abstellanlage` if not available                                                    |
| betreiber                      | string                                   | ?           | operator_name                                     | Omit if not available                                                                           |
| kapazitaet                     | integer                                  | 1           | capacity                                          |                                                                                                 |
| anzahl_lademoeglichkeiten      | integer                                  | ?           | [restrictions](#ParkingSiteRestriction)           | Map to `CHARGING` restriction if > 0                                                            |
| kapazitaet_lastenraeder        | integer                                  | ?           | [restrictions](#ParkingSiteRestriction)           | Map to `CARGOBIKE` restriction if > 0                                                           |
| ueberwacht                     | [Ueberwachung](#Ueberwachung)            | 1           | supervision_type                                  | See [Ueberwachung](#Ueberwachung)                                                               |
| abstellanlagen_ort             | [AbstellanlagenOrt](#AbstellanlagenOrt)  | 1           | related_location, park_and_ride_type              | See [AbstellanlagenOrt](#AbstellanlagenOrt); `BIKE_AND_RIDE` maps to `park_and_ride_type.[YES]` |
| stellplatzart                  | [Stellplatzart](#Stellplatzart)          | 1           | type, purpose                                     | See [Stellplatzart](#Stellplatzart); `SCHLIESSFACH` maps to `purpose.ITEM`                      |
| ueberdacht                     | boolean                                  | 1           | is_covered                                        |                                                                                                 |
| gebuehren_pro_tag              | integer                                  | ?           | has_fee                                           | See [Gebühren](#Gebühren)                                                                       |
| gebuehren_pro_monat            | integer                                  | ?           | has_fee                                           | See [Gebühren](#Gebühren)                                                                       |
| gebuehren_pro_jahr             | integer                                  | ?           | has_fee                                           | See [Gebühren](#Gebühren)                                                                       |
| beschreibung_gebuehren         | string                                   | ?           | fee_description                                   |                                                                                                 |
| beschreibung                   | string                                   | ?           | description                                       | Combined with `weitere_information` (see below)                                                 |
| weitere_information            | string                                   | ?           | description                                       | Appended to `beschreibung`, separated by a space, if present                                    |
| photo_url                      | string                                   | ?           | photo_url                                         |                                                                                                 |
| groessenklasse                 | string                                   | ?           | tags                                              | Prefixed with `BW_SIZE_`, so `BASISANGEBOT_XS` becomes `BW_SIZE_BASISANGEBOT_XS`                |
| zuletzt_bearbeitet_am          | datetime                                 | 1           | static_data_updated_at                            |                                                                                                 |


## Stellplatzart

| Key                                       | Mapping              |
|-------------------------------------------|----------------------|
| ANLEHNBUEGEL                              | `STANDS`             |
| FAHRRADBOX                                | `LOCKERS`            |
| VORDERRADANSCHLUSS                        | `WALL_LOOPS`         |
| VORDERRADANSCHLUSS_SICHERUNGSBUEGEL       | `SAFE_WALL_LOOPS`    |
| DOPPELSTOECKIG                            | `TWO_TIER`           |
| FAHRRADPARKHAUS                           | `BUILDING`           |
| SAMMELANLAGE                              | `SHED`               |
| SCHLIESSFACH                              | `LOCKBOX`            |
| ABSTELLFLAECHE                            | `FLOOR`              |
| SONSTIGE                                  | `OTHER`              |


## Ueberwachung

| Key              | Mapping     |
|------------------|-------------|
| KEINE            | `NO`        |
| VIDEO            | `VIDEO`     |
| UNBEKANNT        |             |


## Gebühren

As a fee of `0` means that the parking site is free of charge, `has_fee` is mapped from the three fee fields
`gebuehren_pro_tag`, `gebuehren_pro_monat` and `gebuehren_pro_jahr` as follows:

| Data                                      | Mapping          |
|-------------------------------------------|------------------|
| At least one fee field is set and not `0` | `has_fee: true`  |
| All set fee fields are `0`                | `has_fee: false` |
| All fee fields are `""` or null           | `has_fee` unset  |


## AbstellanlagenOrt

| Key                      | Mapping                                         |
|--------------------------|-------------------------------------------------|
| OEFFENTLICHE_EINRICHTUNG | `Öffentliche Einrichtung`                       |
| BIKE_AND_RIDE            | `Bike and Ride`, `park_and_ride_type: ["YES"]`  |
| SCHULE                   | `Schule`                                        |
| STRASSENRAUM             | `Straßenraum`                                   |
| BILDUNGSEINRICHTUNG      | `Bildungseinrichtung`                           |
| UNBEKANNT                | `Unbekannt`                                     |
| SONSTIGES                | `Sonstiges`                                     |


## ParkingSiteRestriction

| Key                        | Mapping                          |
|----------------------------|----------------------------------|
| anzahl_lademoeglichkeiten  | `restrictions[0].type.CHARGING`  |
| kapazitaet_lastenraeder    | `restrictions[0].type.CARGOBIKE` |
