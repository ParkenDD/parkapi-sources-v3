# Stadt Bielefeld

The City of Bielefeld provides a CSV file (`;` delimited) with static parking site data.

Coordinates are provided as WKT POINT geometry in EPSG:4326 (WGS84).

Static values:

* `purpose` is always `CAR`
* `static_data_updated_at` is set to the moment of import
* `has_realtime_data` is always `false`


| Field              | Type                    | Cardinality | Mapping            | Comment                                                              |
|--------------------|-------------------------|-------------|--------------------|----------------------------------------------------------------------|
| gid                | string                  | 1           | uid                |                                                                      |
| bez                | string                  | 1           | name               | Contains type and name, e.g. "Parkhaus Am Hauptbahnhof"              |
| WKT                | string (WKT POINT)      | 1           | lat, lon           | EPSG:25832, needs transformation to WGS84                            |
| kapazitaet         | integer                 | ?           | capacity           | Often empty                                                          |
| typ                | [Type](#Type)           | 1           | type               |                                                                      |
| hoehe              | string                  | ?           | max_height         | German format with unit, e.g. "2,00 m"; needs parsing                |
| einfahrtshoehe     | float                   | ?           | max_height         | Numeric value in meters, alternative to `hoehe`                      |
| frauen             | [JaNein](#JaNein)       | ?           | capacity_woman     | J/N flag; does not provide a count                                   |
| behinderte         | string                  | ?           | capacity_disabled  | J/N flag or numeric capacity count                                   |
| zufahrt            | string                  | ?           | address            | Access address / description                                         |
| e_ladesaeule       | [JaNein](#JaNein)       | ?           | capacity_charging  | J/N flag; does not provide a count                                   |
| gebuehren          | [Gebuehren](#Gebuehren) | ?           | has_fee            |                                                                      |
| gebuehren_internet | string (url)            | ?           | fee_description    | URL to fee information                                               |
| oeffi              | [JaNein](#JaNein)       | ?           | park_and_ride_type | J → YES, N → NO                                                      |
| kategorie          | string                  | ?           | description        | Usage category, e.g. "Einzelhandel", "Bildung"                       |
| oeff_mo_fr         | string                  | ?           | opening_hours      | Opening hours Monday to Friday, e.g. "7:00 - 21:00" or "durchgehend" |
| oeff_sa            | string                  | ?           | opening_hours      | Opening hours Saturday                                               |
| oeff_so            | string                  | ?           | opening_hours      | Opening hours Sunday                                                 |
| pls_id             | string                  | ?           | -                  | Parking guidance system ID; not used                                 |


### Type

| Key | Mapping                   |
|-----|---------------------------|
| P   | OFF_STREET_PARKING_GROUND |
| H   | CAR_PARK                  |
| T   | UNDERGROUND               |
| PZ  | OFF_STREET_PARKING_GROUND |
| HZ  | CAR_PARK                  |
| TZ  | UNDERGROUND               |


### Gebuehren

| Key                            | Mapping |
|--------------------------------|---------|
| Ja                             | true    |
| J                              | true    |
| Nein                           | false   |
| Ausweis                        | false   |
| Parkscheinautomat, Handyparken | true   |
| (empty)                        | -       |


### JaNein

| Key | Mapping |
|-----|---------|
| J   | true    |
| N   | false   |
