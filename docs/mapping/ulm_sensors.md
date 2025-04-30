# E-Quartiershubs Ulm: static and sensor based data

The city of Ulm has Parking sites for Underground parking lots and normal car parks. 
In these parking spaces, they also use sensors from citysens to monitor some of their single parking spots and parking sites. 

The static data for `ParkingSite` are converted from Excel table to geojson according 
to the mapping in [NormalizedXlsxConverter](https://github.com/mobidata-bw/parkapi-sources-v3/blob/64bfe8c730501a3395e01f703e7b16a649ff6a76/src/parkapi_sources/converters/base_converter/push/normalized_xlsx_converter.py#L28).
Both `ParkingSite` and `ParkingSpot` static geojson are made available at [parkapi-static-data](https://github.com/ParkenDD/parkapi-static-data).


## `ParkingSite` Properties

Each realtime sensor data is mapped to `ParkingSite` as follows.

| Field                         | Type                                         | Cardinality | Mapping                                 | Comment                                                                            |
|-------------------------------|----------------------------------------------|-------------|-----------------------------------------|------------------------------------------------------------------------------------|
| id                            | string                                       | 1           | uid                                     |                                                                                    |
| maxcarparkfull                | integer                                      | ?           | realtime_capacity                       |                                                                                    |
| currentcarparkfulltotal       | integer                                      | ?           | realtime_free_capacity                  |                                                                                    |
| timestamp                     | datetime                                     | 1           | realtime_data_updated_at                |                                                                                    |

## `ParkingSpot` Properties

Each realtime sensor data is mapped to `ParkingSpot` as follows.

| Field           | Type                                                | Cardinality | Mapping                                         | Comment                                                                            |
|-----------------|-----------------------------------------------------|-------------|-------------------------------------------------|------------------------------------------------------------------------------------|
| id              | string                                              | 1           | uid                                             |                                                                                    |
| occupied        | [ParkingSpotStatus](#ParkingSpotStatus)             | 1           | realtime_status                                 |                                                                                    |
| timestamp       | datetime                                            | 1           | realtime_data_updated_at                        |                                                                                    |

### ParkingSpotStatus

| Key         | Mapping       |
|-------------|---------------|
| True        | TAKEN         |
| False       | AVAILABLE     |