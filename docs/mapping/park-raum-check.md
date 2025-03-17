# Park.Raum.Check

Park.Raum.Check is a project in Baden-Württemberg, where the on street parking space is monitored. It's basically a
GeoJSON file with `LineString` geometry.

## Properties

A `ParkingRecord` provides static data for a `ParkingSpot`.

| Field           | Type                                                | Cardinality | Mapping                                                                 | Comment                                                                            |
|-----------------|-----------------------------------------------------|-------------|-------------------------------------------------------------------------|------------------------------------------------------------------------------------|
| fid             | integer                                             | 1           | uid                                                                     |                                                                                    |
| bereich         | name                                                | 1           | linear_parking_site.name                                                |                                                                                    |
| kapazität       | string                                              | 1           | linear_parking_site_side.capacity                                       |                                                                                    |
| parkdauer       | numeric, null                                       | ?           | linear_parking_site_side.restricted_to.max_stay                         | Source unit: minutes                                                               |
| bewirtschaftung | [ParkingManagementType](#ParkingManagementType)     | 1           |                                                                         |                                                                                    |
| Kommentar       | string, null                                        | ?           | linear_parking_site.description                                         |                                                                                    |
| Erhebung        | string                                              | 1           |                                                                         | date in format dd.mm.yyyy                                                          |
| Kommune         | string                                              | 1           | linear_parking_site.name                                                |                                                                                    |
| Ortsbezug       | string                                              | 1           |                                                                         | always "Straßenraum"                                                               |
| Parkrichtung    | [ParkingDirection](#ParkingDirection), string, null | 1           | linear_parking_site_side.orientation or linear_parking_site.description | if the value is part of the enum, set orientation, otherwise add it to description |
| mittl_Belegung  | numeric                                             | 1           |                                                                         | 0-1 for 0 % - 100 %, 999 as error code                                             |
| max_Belegung    | numeric                                             | ?           |                                                                         | 0-1 for 0 % - 100 %, 999 as error code                                             |
| PLZ             | string, null                                        | ?           | linear_parking_site.name                                                |                                                                                    |



### ParkingManagementType

| Key | Description          | Effect                                                            |
|-----|----------------------|-------------------------------------------------------------------|
| 0   | Freies Parken        | `linear_parking_site.has_fee` set to `false`                      |
| 1   | Parkschein           | `linear_parking_site.has_fee` set to `true`                       |
| 2   | Parkscheibe          |                                                                   |
| 3   | E-Ladesäule          | `linear_parking_site_side.restricted_to.type` set to `CHARGING`   |
| 4   | Behindertenparkplatz | `linear_parking_site_side.restricted_to.type` set to `DISABLED`   |
| 5   | Privat               | `linear_parking_site_side.restricted_to.type` set to `PRIVATE`    |
| 6   | Halböffentlich       |                                                                   |
| 7   | Carsharing           | `linear_parking_site_side.restricted_to.type` set to `CARSHARING` |
| 9   | Falschparken         | `linear_parking_site_side.restricted_to.type` set to `NO_PARKING` |


### ParkingDirection

| Key         | Mapping       |
|-------------|---------------|
| Querparken  | PERPENDICULAR |
| Längsparken | PARALLEL      |
