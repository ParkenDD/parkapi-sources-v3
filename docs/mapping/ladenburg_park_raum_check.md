# Ladenburg ParkRaumCheck

Ladenburg ParkRaumCheck is a static GeoJSON file.

* `has_realtime_data` is set to `false`
* `static_data_updated_at` is set to the moment of import
* `purpose` is set to `CAR`


| Field               | Type                                | Cardinality | Mapping                | Comment                                                              |
|---------------------|-------------------------------------|-------------|------------------------|----------------------------------------------------------------------|
| Name                | ?                                   | ?           |                        | Always `null`                                                        |
| Adresse             | string                              | 1           | address, name          | `address` is set to "`Adresse`, `Ort`"                               |
| Ort                 | string                              | 1           | address                |                                                                      |
| Widmung             | [Widmung](#Widmung)                 | 1           |                        | Completely in `Bewirtschaftung`                                      |
| Parkrichtung        | [Parkrichtung](#Parkrichtung)       | 1           | orientation            |                                                                      |
| Ortsbezug           | [Ortsbezug](#Ortsbezug)             | 1           |                        |                                                                      |
| Haltestellen-ID     | ?                                   | ?           |                        | Always `null`                                                        |
| Gebühreninformation | string                              | ?           | description            | Various formats, cannot be parsed to more structured information     |
| Bewirtschaftung     | [Bewirtschaftung](#Bewirtschaftung) | 1           | restricted_to.type     |                                                                      |
| Maximale_Parkdauer  | integer                             | ?           | restricted_to.max_stay | Duration in minutes                                                  |
| Kapazität           | string                              | 1           | capacity               |                                                                      |
| Erhebungstag        | string (date)                       | 1           |                        |                                                                      |
| Kommentar           | string                              | ?           | description            | "Zum Erhebungszeitpunkt Baustelle" will be removed, as it's outdated |
| Gebührenpflichtig   | bool                                | 1           | has_fee                | Always false                                                         |


### Widmung

| Key             | Mapping |
|-----------------|---------|
| öffentlich      |         |
| Lademöglichkeit |         |
| Taxi            |         |


### Parkrichtung

| Key             | Mapping       |
|-----------------|---------------|
| Längsparken     | PARALLEL      |
| Senkrechtparken | PERPENDICULAR |
| Schrägparken    | DIAGONAL      |


### Ortsbezug

| Key               | Mapping                   |
|-------------------|---------------------------|
| Straßenraum       | ON_STREET                 |
| Parkierungsanlage | OFF_STREET_PARKING_GROUND |
| Tiefgarage        | UNDERGROUND               |


### Bewirtschaftung

| Key                  | Mapping    |
|----------------------|------------|
| Freies Parken        |            |
| E-Ladesäule          | CHARGING   |
| Parkscheibe          |            |
| Behindertenparkplatz | DISABLED   |
| Carsharing           | CARSHARING |
| Taxi                 | TAXI       |
