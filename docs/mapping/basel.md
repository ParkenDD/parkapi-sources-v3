# Stadt Basel

The City of Basel provides a JSON endpoint with parking site data including realtime availability via the Basel parking guidance system.

Static values:

* `purpose` is always `CAR`
* `type` is always `CAR_PARK`
* `has_realtime_data` is always `true`


| Field            | Type              | Cardinality | Mapping                | Comment                                       |
|------------------|-------------------|-------------|------------------------|-----------------------------------------------|
| id2              | string            | 1           | uid                    |                                               |
| name             | string            | 1           | name                   |                                               |
| geo_point_2d.lat | float             | 1           | lat                    |                                               |
| geo_point_2d.lon | float             | 1           | lon                    |                                               |
| total            | integer           | 1           | capacity               |                                               |
| link             | string (url)      | 1           | public_url             |                                               |
| published        | string (datetime) | 1           | static_data_updated_at | ISO 8601 datetime, milliseconds are discarded |


Realtime values:

* `realtime_data_updated_at` is set to `published`

| Field     | Type              | Cardinality | Mapping                  | Comment                                       |
|-----------|-------------------|-------------|--------------------------|-----------------------------------------------|
| id2       | string            | 1           | uid                      |                                               |
| total     | integer           | 1           | realtime_capacity        |                                               |
| free      | integer           | 1           | realtime_free_capacity   |                                               |
| published | string (datetime) | 1           | realtime_data_updated_at | ISO 8601 datetime, milliseconds are discarded |
