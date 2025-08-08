# Stadt Aalen

The City of Aalen provides an Excel table with some static parking site data and an endpoint with realtime data.

Static values:

* `purpose` is always `CAR`
* `has_realtime_data` is always `True`
* `static_data_updated_at` is set to the moment of import

| Field                                          | Type                                      | Cardinality | Mapping                                 | Comment                                                                                           |
|------------------------------------------------|-------------------------------------------|-------------|-----------------------------------------|---------------------------------------------------------------------------------------------------|
| ID                                             | integer                                   | 1           | uid                                     |                                                                                                   |
| Name                                           | string                                    | 1           | name                                    |                                                                                                   |
| Art der Anlage                                 | [Type](#Type)                             | 1           | type                                    |                                                                                                   |
| Betreiber Name                                 | string                                    | 1           | operator_name                           |                                                                                                   |
| Längengrad                                     | string                                    | 1           | lon                                     | `,` as decimal separator                                                                          |
| Breitengrad                                    | string                                    | 1           | lat                                     | `,` as decimal separator                                                                          |
| Adresse - Straße und Nummer                    | string                                    | 1           | address                                 |                                                                                                   |
| Adresse - PLZ und Stadt                        | string                                    | 1           | address                                 |                                                                                                   |
| Anzahl Stellplätze                             | integer                                   | 1           | capacity                                |                                                                                                   |
| Überwacht?                                     | [SupervisionType](#SupervisionType)       | 1           | supervision_type                        |                                                                                                   |
| Überdacht?                                     | boolean                                   | 1           | is_covered                              |                                                                                                   |
| Gebührenpflichtig?                             | boolean                                   | 1           | has_fee                                 |                                                                                                   |
| 24/7 geöffnet?                                 | boolean                                   | 1           | opening_hours                           |                                                                                                   |
| Öffnungszeiten Mo-Fr Beginn                    | string (time)                             | 1           | opening_hours                           |                                                                                                   |
| Öffnungszeiten Mo-Fr Ende                      | string (time)                             | 1           | opening_hours                           |                                                                                                   |
| Öffnungszeiten Sa Beginn                       | string (time)                             | 1           | opening_hours                           |                                                                                                   |
| Öffnungszeiten Sa Ende                         | string (time)                             | 1           | opening_hours                           |                                                                                                   |
| Öffnungszeiten So Beginn                       | string (time)                             | 1           | opening_hours                           |                                                                                                   |
| Öffnungszeiten So Ende                         | string (time)                             | 1           | opening_hours                           |                                                                                                   |
| Foto-URL                                       | string                                    | 1           | photo_url                               |                                                                                                   |
| Webseite                                       | string                                    | 1           | public_url                              |                                                                                                   |
| Park+Ride?                                     | [ParkAndRideType](#ParkAndRideType)       | 1           | park_and_ride_type                      |                                                                                                   |
| Beschreibung                                   | string                                    | 1           | description                             |                                                                                                   |
| Einfahrtshöhe                                  | integer                                   | 1           | max_height                              |                                                                                                   |
| Zweck der Anlage                               | [PurposeType](#PurposeType)               | 1           | purpose                                 |                                                                                                   |
| Anzahl Stellplätze Carsharing                  | integer                                   | 1           | capacity_carsharing                     |                                                                                                   |
| Anzahl Stellplätze Frauen                      | integer                                   | 1           | capacity_woman                          |                                                                                                   |
| Anzahl Stellplätze Behinderte                  | integer                                   | 1           | capacity_disabled                       |                                                                                                   |
| Anzahl Stellplätze Lademöglichkeit             | integer                                   | 1           | capacity_charging                       |                                                                                                   |
| Anzahl Stellplätze Familien                    | integer                                   | 1           | capacity_family                         |                                                                                                   |
| Anzahl Stellplätze Bus                         | integer                                   | 1           | capacity_bus                            |                                                                                                   |
| Anzahl Stellplätze Lastwagen                   | integer                                   | 1           | capacity_truck                          |                                                                                                   |
| Anlage beleuchtet?                             | boolean                                   | 1           | has_lighting                            |                                                                                                   |
| Ortsbezug                                      | string                                    | 1           | related_location                        |                                                                                                   |
| Gebühren-Informationen                         | string                                    | 1           | fee_description                         |                                                                                                   |
| Maximale Parkdauer                             | integer                                   | 1           | max_stay                                |                                                                                                   |


Realtime values:

* `has_realtime_data` is always `True`
* `realtime_data_updated_at` is set to the moment of import

| Field                                          | Type                                      | Cardinality | Mapping                                 | Comment                                                                                                 |
|------------------------------------------------|-------------------------------------------|-------------|-----------------------------------------|---------------------------------------------------------------------------------------------------------|
| name                                           | string                                    | 1           | uid                                     | The `uid` in the static data are in the `name` of the realtime data, therefore we match them together   |
| status                                         | [OpeningStatus](#OpeningStatus)           | 1           | realtime_opening_status                 |                                                                                                         |
| max                                            | integer                                   | 1           | realtime_capacity                       |                                                                                                         |
| free                                           | integer                                   | 1           | realtime_free_capacity                  |                                                                                                         |


### PurposeType

| Key          | Mapping   |
|--------------|-----------|
| Auto         | CAR       |


### Type

| Key                  | Mapping                      |
|----------------------|------------------------------|
| abseits der Straße   | OFF_STREET_PARKING_GROUND    |
| Parkhaus             | CAR_PARK                     |
| Tiefgarage           | UNDERGROUND                  |
| am Straßenrand       | ON_STREET                    |
| andere               | OTHER                        |


### ParkAndRideType

| Key                   | Mapping       |
|-----------------------|---------------|
| ja                    | YES           |
| nein                  | NO            |
| Bahn                  | TRAIN         |
| Bus                   | BUS           |
| Straßenbahn           | TRAM          |
| Fahrgemeinschaft      | CARPOOL       |


### SupervisionType

| Key                   | Mapping       |
|-----------------------|---------------|
| ja                    | YES           |
| nein                  | NO            |
| Video                 | VIDEO         |
| Bewacht               | ATTENDED      |


### OpeningStatus

| Key              | Mapping   |
|------------------|-----------|
| geöffnet         | OPEN      |
| besetzt          | OPEN      |
| geschlossen      | CLOSED    |


