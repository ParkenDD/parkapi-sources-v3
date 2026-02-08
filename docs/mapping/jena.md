# Stadt Jena

The City of Jena provides a GeoJSON FeatureCollection with static parking site data via a WFS endpoint.

Coordinates are provided as GeoJSON Point geometry in EPSG:4326 (WGS84).

Static values:

* `purpose` is always `CAR`
* `static_data_updated_at` is set to the moment of import
* `has_realtime_data` is always `false`


| Field    | Type          | Cardinality | Mapping            | Comment                                                                         |
|----------|---------------|-------------|--------------------|---------------------------------------------------------------------------------|
| id       | integer       | 1           | uid                |                                                                                 |
| gid      | integer       | 1           | -                  | Same value as `id`; not used                                                    |
| name     | string        | 1           | name               |                                                                                 |
| art      | [Art](#Art)   | 1           | type, restrictions | Parking type category; may also define a restriction type                       |
| the_geom | GeoJSON Point | 1           | -                  | Duplicate geometry in EPSG:25832; not used (main geometry from feature is used) |
| geometry | GeoJSON Point | 1           | lat, lon           | EPSG:4326                                                                       |


### Art

| Key                                           | Type                      | Restriction |
|-----------------------------------------------|---------------------------|-------------|
| Parkplatz                                     | OFF_STREET_PARKING_GROUND | -           |
| Parkhaus                                      | CAR_PARK                  | -           |
| Rollstuhlfahrerparkplatz (Anzahl Stellplätze) | ON_STREET                 | DISABLED    |
| Busparkplatz                                  | OFF_STREET_PARKING_GROUND | BUS         |
