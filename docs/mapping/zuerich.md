# Parkleitsystem Stadt Zürich

The PLS Parkleitsystem Zürich AG publishes realtime parking site data as an [RSS feed](https://www.pls-zh.ch/plsFeed/rss)
under the license CC-0, see [data.stadt-zuerich.ch](https://data.stadt-zuerich.ch/dataset/parkleitsystem).

Static data is not provided in a machine-readable format. It was converted from the former
[ParkAPI2-sources](https://github.com/ParkenDD/ParkAPI2-sources) GeoJSON and is made available as static GeoJSON at
[parkapi-static-data](https://github.com/ParkenDD/parkapi-static-data).


## Static values

* `purpose` is always `CAR`
* `has_realtime_data` is always `true`
* `uid` is the `pid` query parameter of the parking site link, e.g. `accu` for
  `https://www.pls-zh.ch/parkhaus/accu.jsp?pid=accu`
* `Parkplatz Theater 11` was added with coordinates from OpenStreetMap


## Realtime values

Each `<item>` of the feed is one parking site.

* `<description>` looks like `open /   41`: the part before `/` is the status, the part after `/` is the free capacity
* parking sites with a status other than `open` or `closed`, e.g. `????`, are skipped

| Field                       | Type              | Cardinality | Mapping                                           | Comment                     |
|-----------------------------|-------------------|-------------|---------------------------------------------------|-----------------------------|
| `link`                      | string (url)      | 1           | uid                                               | `pid` query parameter       |
| `description` (before `/`)  | string            | 1           | [realtime_opening_status](#RealtimeOpeningStatus) |                             |
| `description` (after `/`)   | integer           | ?           | realtime_free_capacity                            |                             |
| `dc:date`                   | string (datetime) | 1           | realtime_data_updated_at                          | ISO 8601 datetime in UTC    |
| `title`                     | string            | 1           | -                                                 | `<name> / <address>`        |


### RealtimeOpeningStatus

| Key      | Mapping | Comment            |
|----------|---------|--------------------|
| `open`   | OPEN    |                    |
| `closed` | CLOSED  |                    |
| other    | -       | dataset is skipped |
