# Freiburg disabled parking spots with sensors

Freiburg provides a GeoJSON with sensor-enabled parking spots.


* `restricted_to.type` is set to `DISABLED`
* `purpose` is set to `CAR`
* `has_realtime_data` is set to `true`
* `static_data_updated_at` is set to the moment of import
* `realtime_data_updated_at` is set to the moment of import

## Properties

| Field     | Type              | Cardinality | Mapping         | Comment                                                       |
|-----------|-------------------|-------------|-----------------|---------------------------------------------------------------|
| name      | string            | 1           | uid, name       | Format: `short name - name`. short name is used as `uid`      |
| adresse   | string            | 1           | address         | Emptystring will be mapped to `None`. `, Germany` is removed. |
| status    | [Status](#Status) | 1           | realtime_status |                                                               |


### Status

| Key | Mapping   |
|-----|-----------|
| 0   | AVAILABLE |
| 1   | TAKEN     |
