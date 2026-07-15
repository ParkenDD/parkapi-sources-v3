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
| Parkplatz-Typ            | [ParkplatzTyp](#ParkplatzTyp) | 1           | name, purpose, type or restrictions  | See ParkplatzTyp below                           |
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
* The `name` is mapped from `Parkplatz-Typ` if not specified otherwise

| Key                                                                                 | Effect                           |
|-------------------------------------------------------------------------------------|----------------------------------|
| Parkplatz für die Öffentlichkeit ohne Beschränkungen                                | name = `Straßen-Parkplatz`       |
| Parkplatz für die Öffentlichkeit mit Parkschein                                     | name = `Straßen-Parkplatz`       |
| Parkplatz für die Öffentlichkeit mit sonstigen Beschränkungen                       | name = `Straßen-Parkplatz`       |
| Bewohner-Parkplatz                                                                  | restrictions[0].type = RESIDENT  |
| Bewohner-Parkplatz sowie mit Parkschein auch für die Öffentlichkeit                 | restrictions[0].type = RESIDENT  |
| Bewohner-Parkplatz sowie mit sonstigen Beschränkungen auch für die Öffentlichkeit   | restrictions[0].type = RESIDENT  |
| Bewohner-Parkplatz mit Beschränkungen                                               | restrictions[0].type = RESIDENT  |
| Behinderten-Parkplatz allgemein                                                     | restrictions[0].type = DISABLED  |
| Behinderten-Parkplatz beschränkt auf bestimmte Zeiten, sonst für die Öffentlichkeit | restrictions[0].type = DISABLED  |
| Behinderten-Parkplatz beschränkt auf bestimmte Zeiten, sonst nur für Bewohner       | restrictions[0].type = DISABLED  |
| Behinderten-Parkplatz beschränkt auf bestimmte Zeiten, sonst für Taxi               | restrictions[0].type = DISABLED  |
| Behinderten-Parkplatz für bestimmte Parkausweis-Nummer                              | restrictions[0].type = DISABLED  |
| Motorrad-Parkplatz                                                                  | purpose = MOTORCYCLE             |
| Carsharing-Stellplatz                                                               | restrictions[0].type = CARSHARING |
| Taxi-Stellplatz                                                                     | restrictions[0].type = TAXI      |
| Parkplatz für Elektrofahrzeuge während des Ladevorgangs                             | restrictions[0].type = CHARGING  |
| Wohnmobil-Parkplatz                                                                 | restrictions[0].type = CARAVAN   |
| Omnibus-Parkplatz                                                                   | restrictions[0].type = BUS       |
| Lkw-Parkplatz                                                                       | restrictions[0].type = TRUCK     |
| Parkplatz privat betrieben für die Öffentlichkeit                                   | name = `Parkplatz`, type = OFF_STREET_PARKING_GROUND |
| Parkhaus oder Tiefgarage privat betrieben für die Öffentlichkeit                    | name = `Parkhaus`, type = CAR_PARK |
| Wanderparkplatz                                                                     | ignored                          |
| Privater Parkplatz                                                                  | ignored                          |
| Behinderten-Parkplatz privat                                                        | ignored                          |
| Parkplatz für Elektrofahrzeuge während des Ladevorgangs privat                      | ignored                          |
| Parkplatz wegen Baustelle zurzeit nicht verfügbar                                   | -                                |
| Parkplatz ungeklärt                                                                 | ignored                          |
| Kein Parkplatz                                                                      | ignored                          |
| null                                                                                | ignored                          |
