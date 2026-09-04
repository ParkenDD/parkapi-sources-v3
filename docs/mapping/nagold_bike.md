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


## Mapping checked against the sample data

The mapping was verified against `tests/converters/data/nagold_bike.geojson` (37 features, exported 2025). 36 features
are integrated, one of them additionally as lockers, which results in 37 `ParkingSite`s and no import errors.

Confirmed by the sample data:

* `OBJECTID`, `Strasse`, `Anzahl_Bue` and `last_edi_1` are set on every real feature, all other fields can be blank.
* `Stellplatz` only uses `Anlehnbügel` (22×) and `Vorderradanschluss` (14×).
* `Beleuchtun`, `Ueberdachu`, `Bike_and_R`, `Immer_geoe` and `Ueberwachu` only use `ja`, `nein` and `" "`.
* Exactly one feature (`OBJECTID` 2412) is the fully blank surveying artifact described above, and it is the only
  feature without capacity.
* Exactly one feature (`OBJECTID` 412) has lockers and charging points.

Not covered by the sample data, so mapped but unverified:

* `Vorderradhalter mit Rahmen-Sicherung` does not occur; the value is taken from the data owner's list of stand types.
* `"Betreiber": "privat"` does not occur; the only operators in the sample are `Edeka`, `Sparkasse` and `Stadt Nagold`.
* `Gebueren_p`, `Gebueren_1` and `Gebueren_2` are blank in every feature, so the fee mapping is based on the field
  names alone.


## Open questions

Points which are not covered by this mapping yet and should be clarified with the data owner:

* `Anzahl_Sch` is assumed to count lockers (Schließfächer). The field is zero for all but one feature of the sample
  data, so the meaning is not confirmed.
* The `Gebueren_*` mapping is unverified, see [Gebuehren](#gebuehren). It is also unclear whether `Gebueren_1` and
  `Gebueren_2` are two separate fee texts or a single text split across two columns, and whether a fee text without
  `Gebueren_p` should imply `has_fee: true`. Should `Gebueren_p` turn out to be free text rather than `ja`/`nein`, the
  affected features are reported as import errors.
* Fees and all other attributes are applied to the bike stands and the lockers alike, although in practice lockers are
  much more likely to be chargeable than the stands next to them. The source has no way to distinguish the two.
* `Anzahl_Lad` is currently mapped to the bike stands. In the single sample feature which has both, the number of
  charging points equals the number of lockers, which suggests the charging points may belong to the lockers instead.
* There is no defined fallback for an unknown or blank `Stellplatz` on a feature that does have capacity. Such
  features are currently reported as import errors. `OTHER` would be an alternative, but silently degrades data
  quality.
* `Immer_geoe: nein` currently results in no `opening_hours` at all. The dataset carries no actual opening times, so
  either the value should be dropped from the source or real opening hours should be added.
* `name` is only the street name and therefore not unique — several installations share e.g. "Marktstraße" (6×) or
  "Am Schloßberg" (4×). Combining `Strasse` and `Lagebeschr` would produce more readable and distinguishable names.
* `address` has no house number, as the source provides none.
* `Eigentueme` (owner) is ignored. It carries the same value as `Betreiber` in all features which have one, so it is
  unclear whether the fields are maintained separately at all, and whether `"Eigentuemer": "privat"` should exclude a
  feature as well.
* `Einbauart`, `Status`, `Gemarkung`, `Maengelbes`, `Sonstige_B` and `Beschrei_1` are ignored. Especially `Status`
  (`Bestand` in the sample data) may need filtering once other values such as planned or dismantled installations
  appear. `Sonstige_B` holds a maintenance note in one feature ("Keine Hinweisschilder auf Ladestation") and could
  become part of `description`. `Beschrei_1` directly follows `Gebueren_2` in the source and may well be the fee
  description, but it is blank everywhere.
* `last_edi_1` is a date at UTC midnight rather than a real timestamp, so `static_data_updated_at` is up to a day off.
