### Esslingen

Esslingen provides its parking spots as GeoJSON with polygons. Coordinates are in UTM32 and have to be transformed to
WSG84.

* `has_realtime_data` is always false

## Properties

| Field                    | Type                          | Cardinality | Mapping                              | Comment                                          |
|--------------------------|-------------------------------|-------------|--------------------------------------|--------------------------------------------------|
| Anzahl der Stellplätze   | integer                       | 1           | capacity                             |                                                  |
| Ausrichtung              | [Ausrichtung](#Ausrichtung)   | ?           | orientation                          |                                                  |
| Bemerkungen              | string                        | ?           | description                          |                                                  |
| Beschränkung sonstig     | string                        | ?           | description                          |                                                  |
| fid                      | integer                       | 1           | uid                                  |                                                  |
| Fläche                   | float                         | 1           |                                      |                                                  |
| Frei für Parkausweis-Nr  | string                        | ?           | description                          |                                                  |
| Parkerlaubnis zeitlich   | string                        | ?           | description                          |                                                  |
| Parkplatz-Typ            | [ParkplatzTyp](#ParkplatzTyp) | 1           | name, purpose, type or restricted_to | See ParkplatzTyp below                           |
| Parkscheibe erforderlich | string                        | ?           | description                          |                                                  |
| Parkschein erforderlich  | string                        | ?           | fee_description, has_fee             | has_fee is set to true if this field is not null |
| Überprüfungsdatum        | date                          | 1           | static_data_updated_at               |                                                  |


### Ausrichtung


| Key         | Mapping  |
|-------------|----------|
| längs       | PARALLEL |
| quer        | DIAGONAL |
| undefiniert |          |
| unbekannt   |          |


### ParkplatzTyp

* The `purpose` is `CAR` if not specified otherwise.
* The `type` is `ON_STREET` if not specified otherwise

| Key                                                                                 | Effect                           |
|-------------------------------------------------------------------------------------|----------------------------------|
| Parkplatz für die Öffentlichkeit ohne Beschränkungen                                | -                                |
| Parkplatz für die Öffentlichkeit mit Parkschein                                     | -                                |
| Parkplatz für die Öffentlichkeit mit sonstigen Beschränkungen                       | -                                |
| Bewohner-Parkplatz                                                                  | restricted_to.type = RESIDENT    |
| Bewohner-Parkplatz sowie mit Parkschein auch für die Öffentlichkeit                 | -                                |
| Bewohner-Parkplatz sowie mit sonstigen Beschränkungen auch für die Öffentlichkeit   | -                                |
| Bewohner-Parkplatz mit Beschränkungen                                               | -                                |
| Behinderten-Parkplatz allgemein                                                     | restricted_to.type = DISABLED    |
| Behinderten-Parkplatz beschränkt auf bestimmte Zeiten, sonst für die Öffentlichkeit | restricted_to.type = DISABLED    |
| Behinderten-Parkplatz beschränkt auf bestimmte Zeiten, sonst nur für Bewohner       | restricted_to.type = DISABLED    |
| Behinderten-Parkplatz beschränkt auf bestimmte Zeiten, sonst für Taxi               | restricted_to.type = DISABLED    |
| Behinderten-Parkplatz für bestimmte Parkausweis-Nummer                              | restricted_to.type = DISABLED    |
| Motorrad-Parkplatz                                                                  | purpose = MOTORCYCLE             |
| Carsharing-Stellplatz                                                               | restricted_to.type = CARSHARING  |
| Taxi-Stellplatz                                                                     | restricted_to.type = TAXI        |
| Parkplatz für Elektrofahrzeuge während des Ladevorgangs                             | restricted_to.type = CHARGING    |
| Wohnmobil-Parkplatz                                                                 | restricted_to.type = CARAVAN     |
| Omnibus-Parkplatz                                                                   | restricted_to.type = BUS         |
| Lkw-Parkplatz                                                                       | restricted_to.type = TRUCK       |
| Parkplatz privat betrieben für die Öffentlichkeit                                   | type = OFF_STREET_PARKING_GROUND |
| Parkhaus oder Tiefgarage privat betrieben für die Öffentlichkeit                    | type = CAR_PARK                  |
| Wanderparkplatz                                                                     | ignored                          |
| Privater Parkplatz                                                                  | ignored                          |
| Behinderten-Parkplatz privat                                                        | ignored                          |
| Parkplatz für Elektrofahrzeuge während des Ladevorgangs privat                      | ignored                          |
| Parkplatz wegen Baustelle zurzeit nicht verfügbar                                   | -                                |
| Parkplatz ungeklärt                                                                 | ignored                          |
| Kein Parkplatz                                                                      | ignored                          |
| null                                                                                | ignored                          |
