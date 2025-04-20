# Freiburg static disabled parking spots

Freiburg provides a GeoJSON with static parking spots.

## Properties

| Field      | Type   | Cardinality | Mapping     | Comment |
|------------|--------|-------------|-------------|---------|
| fid        | string | 1           | uid         |         |
| strasse    | string | 1           | address     |         |
| hausnummer | string | 1           | address     |         |
| anzahl     | string | 1           |             |         |
| hinweis    | string | 1           | description |         |
| stadtteil  | string | 1           |             |         |
