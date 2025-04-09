# E-Quartiershubs Ulm: static and sensor based data

The city of Ulm has Parking sites for Underground parking lots and normal car parks. 
In these parking spaces, they also use sensors from citysens to monitor some of their single parking spots. 

The static data are mapped according to the mapping in [NormalizedXlsxConverter](https://github.com/mobidata-bw/parkapi-sources-v3/blob/64bfe8c730501a3395e01f703e7b16a649ff6a76/src/parkapi_sources/converters/base_converter/push/normalized_xlsx_converter.py#L28)

## Properties

Each sensor data is mapped to `ParkingSpot`.

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