# Park.Raum.Check

Park.Raum.Check is a project in Baden-Württemberg, where the on street parking space is monitored. It's basically a
GeoJSON file. `ParkRaumCheckSachsenheimOnStreetPushConverter` and `ParkRaumCheckKehlPushConverter` uses
`LineString`s and EPSG:3857, `ParkRaumCheckSachsenheimOffStreetPushConverter` uses `Polygon`s and EPSG:4326.


## Properties

A `ParkingRecord` provides static data for a `ParkingSite`.

| Field               | Type                                            | Cardinality | Mapping                  | Comment                          |
|---------------------|-------------------------------------------------|-------------|--------------------------|----------------------------------|
| fid                 | integer                                         | 1           | uid                      |                                  |
| Name                | string                                          | 1           | name                     |                                  |
| Adresse             | string                                          | 1           | address                  |                                  |
| Ort                 | string                                          | 1           | address                  |                                  |
| Widmung             | [SachsenheimDedication](#SachsenheimDedication) | 1           |                          |                                  |
| Parkrichtung        | [ParkingOrientation](#ParkingOrientation)       | ?           | orientation              | In Sachsenheim, cardinality is 1 |
| Ortsbezug           | [SachsenheimLocation](#SachsenheimLocation)     | 1           | type, park_and_ride_type |                                  |
| Haltestellen-ID     | string                                          | ?           | external_identifiers     |                                  |
| Gebührenpflichtig   | bool                                            | 1           | has_fee                  |                                  |
| Gebühreninformation | string                                          | ?           | fee_description          |                                  |
| Bewirtschaftung     | [ParkingManagementType](#ParkingManagementType) | 1           | restrictions.type        |                                  |
| Maximale_Parkdauer  | integer                                         | ?           | restrictions.max_stay    | Used in Sachsenheim              |
| Max. Parkdauer      | integer                                         | ?           | restrictions.max_stay    | Used in Kehl                     |
| Kapazität           | integer                                         | 1           | capacity                 |                                  |
| Erhebungstag        | string (date)                                   | 1           |                          |                                  |
| Kommentar           | string                                          | ?           | description              |                                  |


### SachsenheimDedication

| Key                    | Effect                                |
|------------------------|---------------------------------------|
| öffentlich             |
| privat                 | Datasets are ignored due missing data |
| behinderten Stellplatz |                                       |
| Lademöglichkeit        | Used in Sachsenheim                   |
| E-Ladesäule            | Used in Kehl                          |


### SachsenheimLocation

| Key         | Mapping                                                                      |
|-------------|------------------------------------------------------------------------------|
| P+R         | `type` set to `OFF_STREET_PARKING_GROUND`, `park_and_ride_type` set to `YES` |
| Parkplatz   | `type` set to `OFF_STREET_PARKING_GROUND`                                    |
| Straßenraum | `type` set to `ON_STREET`                                                    |
| Bahnhof     | `type` set to `OFF_STREET_PARKING_GROUND`                                    |
| Parkhaus    | `type` set to `CAR_PARK`                                                     |
| Parkdeck    | `type` set to `CAR_PARK`                                                     |


### ParkingOrientation

| Key             | Mapping       | Comment           |
|-----------------|---------------|-------------------|
| Querparken      | PERPENDICULAR |                   |
| Längsparken     | PARALLEL      |                   |
| Senkrechtparken | PERPENDICULAR |                   |
| Schrägparken    | DIAGONAL      |                   |
| Keine           | None          | Used in Kehl only |


### ParkingManagementType

| Key                  | Comment                      |
|----------------------|------------------------------|
| Freies Parken        |                              |
| Parkscheibe          |                              |
| Behindertenparkplatz | `restrictions` to `DISABLED` |
| E-Ladesäule          | `restrictions` to `CHARGING` |
| Parkschein           | Used in Kehl only            |
| Halböffentlich       | Used in Kehl only            |
