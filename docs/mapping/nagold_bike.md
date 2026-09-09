# Nagold Bike Parking

The city of Nagold publishes a GeoJSON dataset with locations of bicycle parking installations across the city. Each
feature describes a group of bicycle stands or racks available for public use.

Missing values are represented as `null`, but a single blank (`" "`) is treated as "no value" as well. For the required
fields `Strasse` and `Stellplatzart` a missing value is an import error, unless the feature is skipped as described
below.


## `ParkingSite` Properties

Each bicycle parking installation is mapped to a static `ParkingSite` as follows.

Features which are not integrated:

* Parking installations whose `Betreiber` is `privat` are not public parking and are skipped. The value is compared
  case-insensitively and without surrounding whitespace, but has to be exactly `privat`: an operator like
  `privat (Anwohner)` is integrated as usual.
* Features without a stand type and without capacity (`Stellplatzart` empty and `"Anzahl_Buegel_Stellplaetze": 0`) are
  surveying artifacts. They are silently skipped and not reported as import errors. All other fields of such a feature
  are ignored, even if they carry values.

A feature with `Anzahl_Schliessfaecher` greater than zero describes two installations at the same location: the bike
stands and additional lockers. As both have their own type and capacity, they are mapped to two separate
`ParkingSite`s, see [Lockers](#lockers).

Attributes which are set statically by the converter:

* `has_realtime_data` is always set to `false`
* `purpose` is always set to `BIKE`
* `opening_hours` is set to `24/7` when `Immer_geoeffnet_zugaenglich` is `ja`, and left empty otherwise
* `lat` and `lon` are set from the standard GeoJSON coordinates point
* `address` is set to `{Strasse}, 72202 Nagold`, as the source has no house numbers

| Field                          | Type                                | Cardinality | Mapping                                 | Comment                                                                                                              |
|--------------------------------|-------------------------------------|-------------|-----------------------------------------|----------------------------------------------------------------------------------------------------------------------|
| OBJECTID                       | integer                             | 1           | uid                                     | Cast to string                                                                                                       |
| Strasse                        | string                              | 1           | name                                    | Street name used as parking facility name, a blank street is an import error                                         |
| Lagebeschreibung               | string                              | ?           | description                             | Parking description (e.g. "Am Parkplatz vom Polizeirevier"), surrounding whitespace is stripped                      |
| coordinates[1]                 | numeric                             | 1           | lat                                     | GeoJSON geometry coordinates index 1, rounded to 7 decimal places (e.g. 48.552221802366965 becomes 48.5522218)       |
| coordinates[0]                 | numeric                             | 1           | lon                                     | GeoJSON geometry coordinates index 0, rounded to 7 decimal places (e.g. 8.7234782203195511 becomes 8.7234782)        |
| Stellplatzart                  | [Stellplatzart](#stellplatzart)     | 1           | type                                    | See [Stellplatzart](#stellplatzart)                                                                                  |
| Anzahl_Buegel_Stellplaetze     | integer                             | 1           | capacity                                | `0` is accepted and results in a `ParkingSite` without capacity, unless the feature is skipped as surveying artifact |
| Anzahl_Schliessfaecher         | integer                             | ?           | capacity                                | Capacity of the separate `LOCKERS` site, see [Lockers](#lockers)                                                     |
| Anzahl_Lademoeglichkeiten      | integer                             | ?           | [restrictions](#parkingsiterestriction) | Map to `CHARGING` restriction if > 0                                                                                 |
| Beleuchtung                    | [Beleuchtung](#beleuchtung)         | ?           | has_lighting                            | See [Beleuchtung](#beleuchtung)                                                                                      |
| Ueberdachung                   | [Ueberdachung](#ueberdachung)       | ?           | is_covered                              | See [Ueberdachung](#ueberdachung)                                                                                    |
| Bike_and_Ride                  | [ParkAndRideType](#parkandridetype) | ?           | park_and_ride_type                      | See [ParkAndRideType](#parkandridetype)                                                                              |
| Ueberwachung                   | [Ueberwachung](#ueberwachung)       | ?           | supervision_type                        | See [Ueberwachung](#ueberwachung)                                                                                    |
| Betreiber                      | string                              | ?           | operator_name                           | Omit if blank; features with `privat` are not integrated at all                                                      |
| Gebueren_pro_Tag_Cent          | integer                             | ?           | has_fee, fee_description                | See [Gebuehren](#gebuehren)                                                                                          |
| Gebueren_pro_Monat_Cent        | integer                             | ?           | has_fee, fee_description                | See [Gebuehren](#gebuehren)                                                                                          |
| Gebueren_pro_Jahr_Cent         | integer                             | ?           | has_fee, fee_description                | See [Gebuehren](#gebuehren)                                                                                          |
| Beschreibung_Kostenkonditionen | string                              | ?           | fee_description                         | See [Gebuehren](#gebuehren)                                                                                          |
| last_edited_date               | integer                             | 1           | static_data_updated_at                  | Convert epoch milliseconds to ISO 8601                                                                               |

Text fields are limited in length, values above the limit are reported as import errors: `Strasse` and `Betreiber` are
limited to 256, `Beschreibung_Kostenkonditionen` to 2048 and `Lagebeschreibung` to 4096 characters.


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


## Stellplatzart

| Key                                  | Mapping           |
|--------------------------------------|-------------------|
| Anlehnbügel                          | `STANDS`          |
| Vorderradanschluss                   | `WALL_LOOPS`      |
| Vorderradhalter mit Rahmen-Sicherung | `SAFE_WALL_LOOPS` |

Any other value is reported as an import error, a missing `Stellplatzart` included. Only the surveying artifacts
described above, which have no `Stellplatzart` and no capacity, are skipped silently.


## Lockers

If `Anzahl_Schliessfaecher` is greater than zero, the feature additionally describes lockers (Schließfächer) at the
same location. They are mapped to a second `ParkingSite` which shares all attributes of the surrounding installation,
with the following exceptions:

| Field        | Mapping                                                                                     |
|--------------|---------------------------------------------------------------------------------------------|
| uid          | `{OBJECTID}-lockers`, to keep it unique against the `ParkingSite` of the bike stands        |
| name         | `{Strasse} (Schließfächer)`, to distinguish both sites at the same coordinates              |
| type         | Always `LOCKERS`, `Stellplatzart` only describes the bike stands                            |
| capacity     | `Anzahl_Schliessfaecher`                                                                    |
| restrictions | Always empty, `Anzahl_Lademoeglichkeiten` is mapped to the `ParkingSite` of the bike stands |


## Gebuehren

The fees are given as amounts in cent per day, month and year. `has_fee` is set to `True` if at least one of them is
greater than zero, and to `False` if all given amounts are zero. If none of the three fields has a value, `has_fee`
stays empty, as the source does not tell if there is a fee.

`fee_description` is built from all amounts greater than zero, formatted in Euro with two decimal places and a German
decimal comma, followed by `Beschreibung_Kostenkonditionen` and joined with `, `. Amounts of zero are omitted; if
there is neither an amount greater than zero nor a description, `fee_description` stays empty.

| `Gebueren_pro_Tag_Cent` | `Gebueren_pro_Monat_Cent` | `Beschreibung_Kostenkonditionen` | `has_fee` | `fee_description`                                            |
|-------------------------|---------------------------|----------------------------------|-----------|--------------------------------------------------------------|
| `100`                   | `1500`                    | Bezahlung nur mit Karte          | `True`    | `1,00 € pro Tag, 15,00 € pro Monat, Bezahlung nur mit Karte` |
| `100`                   | `null`                    | `null`                           | `True`    | `1,00 € pro Tag`                                             |
| `0`                     | `0`                       | `null`                           | `False`   | empty                                                        |
| `null`                  | `null`                    | `null`                           | empty     | empty                                                        |


## ParkAndRideType

| Key  | Mapping   |
|------|-----------|
| ja   | `["YES"]` |
| nein | `["NO"]`  |


## ParkingSiteRestriction

| Key                       | Mapping                                                                       |
|---------------------------|-------------------------------------------------------------------------------|
| Anzahl_Lademoeglichkeiten | `ParkingAudience.CHARGING` with `capacity` set to `Anzahl_Lademoeglichkeiten` |


## Ueberwachung

| Key  | Mapping |
|------|---------|
| ja   | `YES`   |
| nein | `NO`    |
