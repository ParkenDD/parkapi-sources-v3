# Stadt Bonn

The City of Bonn provides a GeoJSON FeatureCollection with static parking site data via a WFS endpoint.

Coordinates are provided as GeoJSON Point geometry in EPSG:4326 (WGS84).

Static values:

* `purpose` is always `CAR`
* `static_data_updated_at` is set to the moment of import
* `has_realtime_data` is always `false`


| Field        | Type          | Cardinality | Mapping  | Comment                                           |
|--------------|---------------|-------------|----------|---------------------------------------------------|
| parkplatz_id | integer       | 1           | uid      |                                                   |
| bezeichnung  | string        | ?           | name     | May be null; 2 features have no name              |
| art          | [Art](#Art)   | 1           | type     | Parking type category                             |
| inhalt       | string        | 1           | -        | Human-readable label for `art`; not used directly |
| geometry     | GeoJSON Point | 1           | lat, lon | EPSG:4326                                         |


### Art

| Key | Label                                    | Mapping                   |
|-----|------------------------------------------|---------------------------|
| 1   | Autoparkplatz                            | OFF_STREET_PARKING_GROUND |
| 2   | Busparkplatz                             | OFF_STREET_PARKING_GROUND |
| 3   | Motorradparkplatz                        | OFF_STREET_PARKING_GROUND |
| 4   | Wohnwagen- und Wohnmobilabstellplätze    | OFF_STREET_PARKING_GROUND |
