# Radolfzell

Radolfzell provides a large GeoJSON with on street `ParkingSite` parking data. The geometry is `MultiLineString` in

* `purpose` is set to `CAR`
* `type` is set to `ON_STREET`

`Özeit MF` means Monday until Friday. 1 is begin, 2 is end. If begin is after end, we ignore the opening times, as it's
ambiguous.

| Field      | Type          | Cardinality | Mapping            | Comment                                                |
|------------|---------------|-------------|--------------------|--------------------------------------------------------|
| 24/7 geöf  | bool          | 1           | opening_hours      | If set to true: opening_hours set to 24/7              |
| Anz Falsch | ?             | ?           |                    | Always null                                            |
| Art_Anlage | string        | ?           |                    | Either 'Parkplatz' or null                             |
| Beleucht   | bool          | 1           | has_lighting       |                                                        |
| gebpflicht | bool          | ?           | has_fee            |                                                        |
| Gebü Info  | string        | ?           | fee_description    |                                                        |
| id         | integer       | ?           | uid                |                                                        |
| Ladeplatz  | integer       | ?           | capacity_charging  |                                                        |
| Längengra  | float         | ?           |                    |                                                        |
| Live-Daten | bool          | ?           |                    | Just false or null                                     |
| Max Dauer  | string        | ?           | max_stay           | Format: `{integer} {min\|Std}`, transformed in integer |                   |
| Max Höh c  | integer       | ?           | max_height         |                                                        |
| Özeit MF1  | string (time) | ?           | opening_hours      | Without seconds                                        |
| Özeit MF2  | string (time) | ?           | opening_hours      | Without seconds                                        |
| Özeit Sa1  | string (time) | ?           | opening_hours      | Without seconds                                        |
| Özeit Sa2  | string (time) | ?           | opening_hours      | Without seconds                                        |
| Özeit So1  | string (time) | ?           | opening_hours      | Without seconds                                        |
| Özeit So2  | string (time) | ?           | opening_hours      | Without seconds                                        |
| P+R        | string        | ?           | park_and_ride_type | if set: `park_and_ride_type = ['YES']`                 |
| Parkscheib | string        | ?           |                    |                                                        |
| Regel_Txt  |               | ?           | description        |                                                        |
| Regelung   | integer       | ?           | resticted_to       |                                                        |
| Richtung   |               | ?           | orientation        |                                                        |
| Stellpl    | integer       | ?           | capacity           | null and 0: Dataset is ignored                         |
| StrPLZOrt2 | string        | ?           | address            |                                                        |
| Weite Info | string        | ?           | description        |                                                        |


### Regelung

| Key | Meaning                                     | Mapping                      |
|-----|---------------------------------------------|------------------------------|
| 1   | Park-/ Halteverbot                          | Dataset is ignored           |
| 2   | Radweg /-schutzstreifen am Fahrbahnrand     | -                            |
| 3   | Verkehrsberuhigter Bereich                  | -                            |
| 4   | Parken innerhalb gekennzeichneter Flächen   | -                            |
| 5   | Parken ohne Parkregelung                    | -                            |
| 5   | Gehwegparken (markiert)                     | -                            |
| 7   | Parken mit Parkschein (Dauerparken)         | -                            |
| 8   | Parken mit Parkscheibe                      | -                            |
| 9   | Parken mit Parkschein (4 Std)               | -                            |
| 10  | Parken mit Parkschein (24 Std)              | -                            |
| 11  | Bewohnerparken                              | resticted_to.type = RESIDENT |
| 12  | Kurzzeitparken (Brötchentaste)              | -                            |
| 13  | Parken mit Parkschein (1 Std)               | -                            |
| 14  | Parken unzulässig (enge Restfahrbahnbreite) | Dataset is ignored           |


### Richtung


| Key | Meaning                                    | Mapping       |
|-----|--------------------------------------------|---------------|
| 1   | Längs-parkende Aufstellfläche Fahrzeug     | PARALLEL      |
| 2   | Quer-parkende Aufstellfläche Fahrzeug      | DIAGONAL      |
| 3   | Senkrecht-parkende Aufstellfläche Fahrzeug | PERPENDICULAR |
