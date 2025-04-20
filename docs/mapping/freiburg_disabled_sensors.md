# Freiburg disabled parking spots with sensors

Freiburg provides a GeoJSON with sensor-enabled parking spots.

## Properties

| Field     | Type              | Cardinality | Mapping         | Comment |
|-----------|-------------------|-------------|-----------------|---------|
| name      | string            | 1           | uid, name       |         |
| adresse   | hausnummer        | 1           | address         |         |
| status    | [Status](#Status) | 1           | realtime_status |         |


### Status

| Key | Mapping   |
|-----|-----------|
| 0   | TAKEN     |
| 1   | AVAILABLE |
