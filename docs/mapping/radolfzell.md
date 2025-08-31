# Radolfzell

Radolfzell provides a large GeoJSON with on street `ParkingSite` parking data. The geometry is `MultiLineString`.

* `purpose` is set to `CAR`
* `has_realtime_data` is set to `false`
* `uid` is set to `{Längengra}_{Breitengrd}`
* `static_data_updated_at` is set to the moment of import

`Özeit MF` means Monday until Friday. 1 is begin, 2 is end. If begin is after end, we ignore the opening times, as it's
ambiguous.

| Field      | Type                            | Cardinality | Mapping                     | Comment                                                                                            |
|------------|---------------------------------|-------------|-----------------------------|----------------------------------------------------------------------------------------------------|
| 24/7 geöf  | bool                            | 1           | opening_hours               | If set to true: opening_hours set to 24/7                                                          |
| Anz Falsch | ?                               | ?           |                             | Always null                                                                                        |
| Art_Anlage | string                          | ?           | type                        | If `Parkplatz`, `OFF_STREET_PARKING_GROUND`, otherwise it's `null`, which is mapped to `ON_STREET` |
| Behindstlp | integer                         | ?           | capacity_disabled           |                                                                                                    |
| Beleucht   | bool                            | 1           | has_lighting                |                                                                                                    |
| Breitengrd | float                           | 1           | lat                         | UTM32, needs to be transformed into WSG84                                                          |
| Carsharing | integer                         | ?           | capacity_carsharing         |                                                                                                    |
| gebpflicht | bool                            | ?           | has_fee                     |                                                                                                    |
| Gebü Info  | string                          | ?           | fee_description             |                                                                                                    |
| id         | integer                         | ?           |                             | If `id` is 0, the dataset should be ignored silently                                               |
| Ladeplatz  | integer                         | ?           | capacity_charging           |                                                                                                    |
| Längengra  | float                           | ?           | lon                         | UTM32, needs to be transformed into WSG84                                                          |
| Live-Daten | bool                            | ?           |                             | Just false or null                                                                                 |
| Max Dauer  | string                          | ?           | max_stay                    | Format: `{integer} {min\|Std}`, transformed in integer                                             |                   |
| Max Höh c  | integer                         | ?           | max_height                  |                                                                                                    |
| Özeit MF1  | string (time)                   | ?           | opening_hours               | Without seconds                                                                                    |
| Özeit MF2  | string (time)                   | ?           | opening_hours               | Without seconds                                                                                    |
| Özeit Sa1  | string (time)                   | ?           | opening_hours               | Without seconds                                                                                    |
| Özeit Sa2  | string (time)                   | ?           | opening_hours               | Without seconds                                                                                    |
| Özeit So1  | string (time)                   | ?           | opening_hours               | Without seconds                                                                                    |
| Özeit So2  | string (time)                   | ?           | opening_hours               | Without seconds                                                                                    |
| P+R        | string                          | ?           | park_and_ride_type          | if set: `park_and_ride_type = ['YES']`                                                             |
| Parkscheib | string                          | ?           |                             |                                                                                                    |
| Regel_Txt  |                                 | ?           | description                 |                                                                                                    |
| Regelung   | integer ([Regelung](#Regelung)) | ?           | restricted_to, parking_type |                                                                                                    |
| Richtung   | integer([Richtung])(#Richtung)) | ?           | orientation                 |                                                                                                    |
| Stellpl    | integer                         | ?           | capacity                    | null and 0: Dataset is ignored                                                                     |
| StrPLZOrt2 | string                          | ?           | name, address               |                                                                                                    |
| Weite Info | string                          | ?           | description                 |                                                                                                    |


### Regelung

| Key | Meaning                                     | Mapping                       |
|-----|---------------------------------------------|-------------------------------|
| 1   | Park-/ Halteverbot                          | Dataset is ignored            |
| 2   | Radweg /-schutzstreifen am Fahrbahnrand     | -                             |
| 3   | Verkehrsberuhigter Bereich                  | -                             |
| 4   | Parken innerhalb gekennzeichneter Flächen   | -                             |
| 5   | Parken ohne Parkregelung                    | -                             |
| 5   | Gehwegparken (markiert)                     | parking_type = ON_KERB        |
| 7   | Parken mit Parkschein (Dauerparken)         | -                             |
| 8   | Parken mit Parkscheibe                      | -                             |
| 9   | Parken mit Parkschein (4 Std)               | -                             |
| 10  | Parken mit Parkschein (24 Std)              | -                             |
| 11  | Bewohnerparken                              | restricted_to.type = RESIDENT |
| 12  | Kurzzeitparken (Brötchentaste)              | -                             |
| 13  | Parken mit Parkschein (1 Std)               | -                             |
| 14  | Parken unzulässig (enge Restfahrbahnbreite) | Dataset is ignored            |


### Richtung


| Key | Meaning                                    | Mapping       |
|-----|--------------------------------------------|---------------|
| 1   | Längs-parkende Aufstellfläche Fahrzeug     | PARALLEL      |
| 2   | Quer-parkende Aufstellfläche Fahrzeug      | DIAGONAL      |
| 3   | Senkrecht-parkende Aufstellfläche Fahrzeug | PERPENDICULAR |
