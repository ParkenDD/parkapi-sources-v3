# Nagold Bike Parking

The city of Nagold publishes a GeoJSON dataset with locations of bicycle parking installations across the city. Each feature describes a group of bicycle stands or racks available for public use.


## `ParkingSite` Properties

Static values:

Each bicycle parking installation is mapped to a static `ParkingSite` as follows.
Parking installations with `"Stellplatz": " "` and `"Anzahl_Bue": 0` should not be integrated. These features are
surveying artifacts in which every text field is blank; they are silently skipped and not reported as import errors.

A feature with `Anzahl_Sch` greater than zero describes two installations at the same location: the bike stands and
additional lockers. As both have their own type and capacity, they are mapped to two separate `ParkingSite`s, see
[Lockers](#Lockers).

The dataset uses a single blank (`" "`) instead of an empty string or `null` for all missing text values, so `" "` has
to be treated as "no value" for every string and enum field.

Attributes which are set statically by the converter:

* `has_realtime_data` is always set to `false`
* `opening_hours` is set to `24/7` when `Immer_geoe` is `ja`, and left empty otherwise
* `purpose` is always set to `BIKE`
* `lat` and `lon` are set from the standard GeoJSON coordinates point
* `address` is set to `{Strasse}, 72202 Nagold`, as the source has no house numbers

| Field          | Type                              | Cardinality | Mapping                                 | Comment                                                      |
|----------------|-----------------------------------|-------------|-----------------------------------------|--------------------------------------------------------------|
| OBJECTID       | integer                           | 1           | uid                                     | Cast to string                                               |
| Strasse        | string                            | 1           | name                                    | Street name used as parking facility name                    |
| Lagebeschr     | string                            | ?           | description                             | Parking description (e.g. "Am Parkplatz vom Polizeirevier")  |
| coordinates[1] | numeric                           | 1           | lat                                     | GeoJSON geometry coordinates index 1                         |
| coordinates[0] | numeric                           | 1           | lon                                     | GeoJSON geometry coordinates index 0                         |
| Stellplatz     | [Stellplatz](#Stellplatz)         | 1           | type                                    | See [Stellplatz](#Stellplatz)                                |
| Anzahl_Bue     | integer                           | 1           | capacity                                |                                                              |
| Anzahl_Sch     | integer                           | ?           | capacity                                | Capacity of the separate `LOCKERS` site, see [Lockers](#Lockers) |
| Anzahl_Lad     | integer                           | 1           | [restrictions](#ParkingSiteRestriction) | Map to `CHARGING` restrictions if > 0                        |
| Beleuchtun     | [Beleuchtung](#Beleuchtung)       | ?           | has_lighting                            | See [Beleuchtung](#Beleuchtung)                              |
| Ueberdachu     | [Ueberdachung](#Ueberdachung)     | ?           | is_covered                              | See [Ueberdachung](#Ueberdachung)                            |
| Bike_and_R     | [Bike_and_Ride](#ParkAndRideType) | ?           | park_and_ride_type                      | See [Bike_and_Ride](#ParkAndRideType)                        |
| Ueberwachu     | [Ueberwachung](#Ueberwachung)     | ?           | supervision_type                        | See [Ueberwachung](#Ueberwachung)                            |
| Betreiber      | string                            | ?           | operator_name                           | Omit if blank                                                |
| Gebueren_p     | [Gebuehren](#Gebuehren)           | ?           | has_fee                                 | See [Gebuehren](#Gebuehren)                                  |
| Gebueren_1     | string                            | ?           | fee_description                         | See [Gebuehren](#Gebuehren)                                  |
| Gebueren_2     | string                            | ?           | fee_description                         | See [Gebuehren](#Gebuehren)                                  |
| last_edi_1     | integer                           | 1           | static_data_updated_at                  | Convert epoch milliseconds to ISO 8601                       |


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


## Lockers

If `Anzahl_Sch` is greater than zero, the feature additionally describes lockers (Schließfächer) at the same location.
They are mapped to a second `ParkingSite` which shares all attributes of the surrounding installation, with the
following exceptions:

| Field           | Mapping                                                                                    |
|-----------------|--------------------------------------------------------------------------------------------|
| uid             | `{OBJECTID}-lockers`, to keep it unique against the `ParkingSite` of the bike stands       |
| name            | `{Strasse} (Schließfächer)`, to distinguish both sites at the same coordinates             |
| type            | Always `LOCKERS`, `Stellplatz` only describes the bike stands                              |
| capacity        | `Anzahl_Sch`                                                                                |
| restrictions    | Always empty, `Anzahl_Lad` is mapped to the `ParkingSite` of the bike stands               |


## Gebuehren

The fee fields are blank for every feature of the source dataset, so this mapping is based on the field names alone
and could not be verified against real values.

`Gebueren_p` is read as a boolean and mapped to `has_fee`:

| Key  | Mapping |
|------|---------|
| ja   | `True`  |
| nein | `False` |

`Gebueren_1` and `Gebueren_2` are read as free text and joined with `, ` into `fee_description`. Blank values are
omitted; if both are blank, `fee_description` stays empty.


## ParkAndRideType

| Key  | Mapping    |
|------|------------|
| ja   | `["YES"]`  |
| nein | `["NO"]`   |


## ParkingSiteRestriction

| Key        | Mapping                                                        |
|------------|----------------------------------------------------------------|
| Anzahl_Lad | `ParkingAudience.CHARGING` with `capacity` set to `Anzahl_Lad` |


## Ueberwachung

| Key  | Mapping |
|------|---------|
| ja   | `YES`   |
| nein | `NO`    |


## Open questions

Points which are not covered by this mapping yet and should be clarified with the data owner:

* `Anzahl_Sch` is assumed to count lockers (Schließfächer). The field is blank or zero for all but one feature of the
  sample data, so the meaning is not confirmed.
* The `Gebueren_*` mapping is unverified, see [Gebuehren](#Gebuehren). It is also unclear whether `Gebueren_1` and
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
* `name` is only the street name and therefore not unique — several installations share e.g. "Lange Straße".
  Combining `Strasse` and `Lagebeschr` would produce more readable and distinguishable names.
* `address` has no house number, as the source provides none.
* `Einbauart`, `Status`, `Gemarkung`, `Maengelbes` and `Beschrei_1` are ignored. Especially `Status` (`Bestand` in the
  sample data) may need filtering once other values such as planned or dismantled installations appear. `Beschrei_1`
  directly follows `Gebueren_2` in the source and may well be the fee description, but it is blank everywhere.
* `last_edi_1` is a date at UTC midnight rather than a real timestamp, so `static_data_updated_at` is up to a day off.
