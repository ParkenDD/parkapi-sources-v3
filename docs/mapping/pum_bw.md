# Park + Mitfahren: Static data of the State of Baden-Württemberg

The Ministry of Transport provides static data on Carpooling along the Autobahn/Highways for Cars.

Attributes which are set statically:

* `has_realtime_data` is always set to `False`
* `type` is always set to `OFF_STREET_PARKING_GROUND`
* `park_and_ride_type` is always set to `['CARPOOL']`


## ParkingSites

A `ParkingSites` provides static data for a `ParkingSite`.

| Field                                                 | Type                     | Cardinality | Mapping                | Comment                                                                                                                 |
|-------------------------------------------------------|--------------------------|-------------|------------------------|-------------------------------------------------------------------------------------------------------------------------|
| Id                                                    | integer                  | 1           | uid                    |                                                                                                                         |
| BAB/B                                                 | string                   | 1           | name                   |                                                                                                                         |
| Nr                                                    | integer                  | 1           | name                   |                                                                                                                         |
| Bezeichnung                                           | string                   | 1           | name                   |                                                                                                                         |
| Anzahl der Pkw-Parkstände                             | integer                  | 1           | capacity               |                                                                                                                         |
| Anbindung über(Str.Nr. Bundes- oder Landesstraße)     | string                   | 1           | description            |                                                                                                                         |
| Breite                                                | string (decimal)         | 1           | latitude               |                                                                                                                         |
| Länge                                                 | string (decimal)         | 1           | longitude              |                                                                                                                         |
| Beleuchtung(vorhanden / nicht vorhanden)              | HasLightingBoolean       | 1           | has_lighting           |                                                                                                                         |
| Google Maps                                           | string                   | 1           | public_url             |  Values here are in excel hyperlinks with prefix `=HYPERLINK`. They are formatted into url strings with prefix `https`  |


#### HasLightingBoolean

| Key                    | Mapping   |
|------------------------|-----------|
| vorhanden              | TRUE      |
| nicht vorhanden        | FALSE     |
| Durchfahrt beleuchtet  | TRUE      |
| k. A.                  |           |
| teilweise beleuchtet   | TRUE      |