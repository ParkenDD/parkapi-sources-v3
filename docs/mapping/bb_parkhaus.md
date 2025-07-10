# B+B Parkhaus GmbH & Co. KG

B+B Parkhaus GmbH & Co. KG provides an Excel table with some static parking site data.

Static values:

* `purpose` is always `CAR`
* `has_realtime_data` is always `false`
* `static_data_updated_at` is set to the moment of import

| Field                                          | Type                                      | Cardinality | Mapping                                 | Comment                                                                                           |
|------------------------------------------------|-------------------------------------------|-------------|-----------------------------------------|---------------------------------------------------------------------------------------------------|
| id                                             | integer                                   | 1           | uid                                     |                                                                                                   |
| Name                                           | string                                    | 1           | name                                    |                                                                                                   |
| Art der Anlage                                 | [Type](#Type)                             | 1           | type                                    |                                                                                                   |
| Betreiber Name                                 | string                                    | 1           | operator_name                           |                                                                                                   |
| Längengrad                                     | string                                    | 1           | lon                                     | `,` as decimal separator                                                                          |
| Breitengrad                                    | string                                    | 1           | lat                                     | `,` as decimal separator                                                                          |
| Adresse mit PLZ und Stadt                      | string                                    | 1           | address                                 |                                                                                                   |
| Maximale Parkdauer                             | integer                                   | 1           | max_stay                                |                                                                                                   |
| Anzahl Stellplätze                             | integer                                   | 1           | capacity                                |                                                                                                   |
| is_supervised                                  | boolean                                   | 1           | supervision_type                        |                                                                                                   |
| is_covered                                     | boolean                                   | 1           | is_covered                              |                                                                                                   |
| Ladeplätze                                     | integer                                   | 1           | capacity_charging                       |                                                                                                   |
| Gebührenpflichtig?                             | boolean                                   | 1           | has_fee                                 |                                                                                                   |
| 24/7 geöffnet?                                 | boolean                                   | 1           | opening_hours                           |                                                                                                   |
| Öffnungszeiten Mo-Fr Beginn                    | string (time)                             | 1           | opening_hours                           |                                                                                                   |
| Öffnungszeiten Mo-Fr Ende                      | string (time)                             | 1           | opening_hours                           |                                                                                                   |
| Öffnungszeiten Sa Beginn                       | string (time)                             | 1           | opening_hours                           |                                                                                                   |
| Öffnungszeiten Sa Ende                         | string (time)                             | 1           | opening_hours                           |                                                                                                   |
| Öffnungszeiten So Beginn                       | string (time)                             | 1           | opening_hours                           |                                                                                                   |
| Öffnungszeiten So Ende                         | string (time)                             | 1           | opening_hours                           |                                                                                                   |
| Webseite                                       | string                                    | 1           | public_url                              |                                                                                                   |
| Park&Ride                                      | [ParkAndRideType](#ParkAndRideType)       | 1           | park_and_ride_type                      |                                                                                                   |
| Weitere öffentliche Informationen              | string                                    | 1           | description                             |                                                                                                   |
| Einfahrtshöhe (cm)                             | integer                                   | 1           | max_height                              |                                                                                                   |
| Zweck der Anlage                               | [PurposeType](#PurposeType)               | 1           | purpose                                 |                                                                                                   |
| Anzahl Carsharing-Parkplätze                   | integer                                   | 1           | capacity_carsharing                     |                                                                                                   |
| Anzahl Frauenparkplätze                        | integer                                   | 1           | capacity_woman                          |                                                                                                   |
| Anzahl Behindertenparkplätze                   | integer                                   | 1           | capacity_disabled                       |                                                                                                   |
| Anlage beleuchtet?                             | boolean                                   | 1           | has_lighting                            |                                                                                                   |
| Existieren Live-Daten?                         | boolean                                   | 1           | has_realtime_data                       |                                                                                                   |

### PurposeType

| Key          | Mapping   |
|--------------|-----------|
| Auto         | CAR       |


### Type

| Key         | Mapping                      |
|-------------|------------------------------|
| Parkplatz   | OFF_STREET_PARKING_GROUND    |
| Parkhaus    | CAR_PARK                     |
| Tiefgarage  | UNDERGROUND                  |


### ParkAndRideType

| Key         | Mapping       |
|-------------|---------------|
| ja          | [YES]         |
| nein        | [NO]          |
