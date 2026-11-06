# Stadt Basel

The City of Basel publishes parking site data of the [Parkleitsystem Basel](https://www.parkleitsystem-basel.ch) as
[JSON export](https://data.bs.ch/api/v2/catalog/datasets/100088/exports/json) at [data.bs.ch](https://data.bs.ch)
under the license CC BY 4.0.

The endpoint is a JSON list. Each item is one parking site and contains both static and realtime data, so static and
realtime data are generated from the same request.


## Ignore rules

* If the config key `PARK_API_BASEL_IGNORE_MISSING_CAPACITIES` is set, parking sites without a `total` are ignored.
  Otherwise, they are reported as validation errors.


## Static values

* `purpose` is always `CAR`
* `type` is always `CAR_PARK`
* `has_realtime_data` is always `true`

| Field              | Type              | Cardinality | Mapping                | Comment                                                                 |
|--------------------|-------------------|-------------|------------------------|-------------------------------------------------------------------------|
| `id2`              | string            | 1           | uid                    |                                                                         |
| `name`             | string            | 1           | name                   |                                                                         |
| `title`            | string            | 1           | -                      | name with prefix, e.g. `Parkhaus Bad. Bahnhof`                          |
| `geo_point_2d.lat` | number            | 1           | lat                    |                                                                         |
| `geo_point_2d.lon` | number            | 1           | lon                    |                                                                         |
| `total`            | integer           | 1           | capacity               | ignored if missing when `PARK_API_BASEL_IGNORE_MISSING_CAPACITIES` set  |
| `link`             | string (url)      | 1           | public_url             |                                                                         |
| `published`        | string (datetime) | 1           | static_data_updated_at | ISO 8601 datetime, UTC if no timezone is given, milliseconds discarded  |


## Realtime values

| Field       | Type              | Cardinality | Mapping                                        | Comment                                                                |
|-------------|-------------------|-------------|------------------------------------------------|------------------------------------------------------------------------|
| `id2`       | string            | 1           | uid                                            |                                                                        |
| `total`     | integer           | 1           | realtime_capacity                              | ignored if missing when `PARK_API_BASEL_IGNORE_MISSING_CAPACITIES` set |
| `free`      | integer           | 1           | realtime_free_capacity                         |                                                                        |
| `status`    | string            | ?           | [realtime_opening_status](#BaselOpeningStatus) |                                                                        |
| `published` | string (datetime) | 1           | realtime_data_updated_at                       | ISO 8601 datetime, UTC if no timezone is given, milliseconds discarded |


### BaselOpeningStatus

| Key           | Mapping | Comment |
|---------------|---------|---------|
| `offen`       | OPEN    |         |
| `geschlossen` | CLOSED  |         |
| other         | -       | ignored |


## Unused fields

The following fields are provided, but not used: `id`, `description`, `anteil_frei`, `auslastung`,
`auslastung_prozent`, `address`, `lot_type` and `last_downloaded`.
