# Nagold Bike Parking

The city of Nagold publishes a GeoJSON dataset with locations of bicycle parking installations across the city. Each
feature describes a group of bicycle stands or racks available for public use.

The dataset is exported from a shapefile-based cadastre, therefore all property names are truncated to ten characters
(`Anzahl_Bue` for `Anzahl_Buegel_Stellplaetze`, `Immer_geoe` for `Immer_geoeffnet_zugaenglich` and so on). The tables
below use the property names as they appear in the GeoJSON.

Missing values are not represented as `null` or as an empty string, but as a single blank (`" "`), so `" "` has to be
treated as "no value" for every string and enum field. For the two required fields `Strasse` and `Stellplatz` a blank
is an import error, unless the feature is skipped as described below.


## `ParkingSite` Properties

Each bicycle parking installation is mapped to a static `ParkingSite` as follows.

Features which are not integrated:

* Parking installations whose `Betreiber` is `privat` are not public parking and are skipped. The value is compared
  case-insensitively and without surrounding whitespace, but has to be exactly `privat`: an operator like
  `privat (Anwohner)` is integrated as usual.
* Features without a stand type and without capacity (`"Stellplatz": " "` and `"Anzahl_Bue": 0`) are surveying
  artifacts. They are silently skipped and not reported as import errors. All other fields of such a feature are
  ignored, even if they carry values.

A feature with `Anzahl_Sch` greater than zero describes two installations at the same location: the bike stands and
additional lockers. As both have their own type and capacity, they are mapped to two separate `ParkingSite`s, see
[Lockers](#lockers).

Attributes which are set statically by the converter:

* `has_realtime_data` is always set to `false`
* `purpose` is always set to `BIKE`
* `opening_hours` is set to `24/7` when `Immer_geoe` is `ja`, and left empty otherwise
* `lat` and `lon` are set from the standard GeoJSON coordinates point
* `address` is set to `{Strasse}, 72202 Nagold`, as the source has no house numbers

| Field          | Type                              | Cardinality | Mapping                                 | Comment                                                                                                                 |
|----------------|-----------------------------------|-------------|-----------------------------------------|-------------------------------------------------------------------------------------------------------------------------|
| OBJECTID       | integer                           | 1           | uid                                     | Cast to string                                                                                                          |
| Strasse        | string                            | 1           | name                                    | Street name used as parking facility name, a blank street is an import error                                            |
| Lagebeschr     | string                            | ?           | description                             | Parking description (e.g. "Am Parkplatz vom Polizeirevier")                                                             |
| coordinates[1] | numeric                           | 1           | lat                                     | GeoJSON geometry coordinates index 1, rounded to 7 decimal places (e.g. 48.552221802366965 becomes 48.5522218)          |
| coordinates[0] | numeric                           | 1           | lon                                     | GeoJSON geometry coordinates index 0, rounded to 7 decimal places (e.g. 8.7234782203195511 becomes 8.7234782)           |
| Stellplatz     | [Stellplatz](#stellplatz)         | 1           | type                                    | See [Stellplatz](#stellplatz)                                                                                           |
| Anzahl_Bue     | integer                           | 1           | capacity                                | `0` is accepted and results in a `ParkingSite` without capacity, unless the feature is skipped as a surveying artifact  |
| Anzahl_Sch     | integer                           | ?           | capacity                                | Capacity of the separate `LOCKERS` site, see [Lockers](#lockers)                                                        |
| Anzahl_Lad     | integer                           | ?           | [restrictions](#parkingsiterestriction) | Map to `CHARGING` restriction if > 0                                                                                    |
| Beleuchtun     | [Beleuchtung](#beleuchtung)       | ?           | has_lighting                            | See [Beleuchtung](#beleuchtung)                                                                                         |
| Ueberdachu     | [Ueberdachung](#ueberdachung)     | ?           | is_covered                              | See [Ueberdachung](#ueberdachung)                                                                                       |
| Bike_and_R     | [Bike_and_Ride](#parkandridetype) | ?           | park_and_ride_type                      | See [Bike_and_Ride](#parkandridetype)                                                                                   |
| Ueberwachu     | [Ueberwachung](#ueberwachung)     | ?           | supervision_type                        | See [Ueberwachung](#ueberwachung)                                                                                       |
| Betreiber      | string                            | ?           | operator_name                           | Omit if blank; features with `privat` are not integrated at all                                                         |
| Gebueren_p     | [Gebuehren](#gebuehren)           | ?           | has_fee                                 | See [Gebuehren](#gebuehren)                                                                                             |
| Gebueren_1     | string                            | ?           | fee_description                         | See [Gebuehren](#gebuehren)                                                                                             |
| Gebueren_2     | string                            | ?           | fee_description                         | See [Gebuehren](#gebuehren)                                                                                             |
| last_edi_1     | integer                           | 1           | static_data_updated_at                  | Convert epoch milliseconds to ISO 8601                                                                                  |

Text fields are limited in length, values above the limit are reported as import errors: `Strasse` and `Betreiber` are
limited to 256, `Gebueren_1` and `Gebueren_2` to 2048 and `Lagebeschr` to 4096 characters.


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

| Key                                  | Mapping           |
|--------------------------------------|-------------------|
| Anlehnbügel                          | `STANDS`          |
| Vorderradanschluss                   | `WALL_LOOPS`      |
| Vorderradhalter mit Rahmen-Sicherung | `SAFE_WALL_LOOPS` |

Any other value is reported as an import error, a blank `Stellplatz` included. Only the surveying artifacts described
above, which have a blank `Stellplatz` and no capacity, are skipped silently.


## Lockers

If `Anzahl_Sch` is greater than zero, the feature additionally describes lockers (Schließfächer) at the same location.
They are mapped to a second `ParkingSite` which shares all attributes of the surrounding installation, with the
following exceptions:

| Field        | Mapping                                                                      |
|--------------|------------------------------------------------------------------------------|
| uid          | `{OBJECTID}-lockers`, to keep it unique against the `ParkingSite` of the bike stands |
| name         | `{Strasse} (Schließfächer)`, to distinguish both sites at the same coordinates |
| type         | Always `LOCKERS`, `Stellplatz` only describes the bike stands                 |
| capacity     | `Anzahl_Sch`                                                                  |
| restrictions | Always empty, `Anzahl_Lad` is mapped to the `ParkingSite` of the bike stands   |


## Gebuehren

`Gebueren_p` is read as a boolean and mapped to `has_fee`:

| Key  | Mapping |
|------|---------|
| ja   | `True`  |
| nein | `False` |

`Gebueren_1` and `Gebueren_2` are read as free text and joined with `, ` into `fee_description`. Blank values are
omitted; if both are blank, `fee_description` stays empty.


## ParkAndRideType

| Key  | Mapping   |
|------|-----------|
| ja   | `["YES"]` |
| nein | `["NO"]`  |


## ParkingSiteRestriction

| Key        | Mapping                                                        |
|------------|----------------------------------------------------------------|
| Anzahl_Lad | `ParkingAudience.CHARGING` with `capacity` set to `Anzahl_Lad` |


## Ueberwachung

| Key  | Mapping |
|------|---------|
| ja   | `YES`   |
| nein | `NO`    |
