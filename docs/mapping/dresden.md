# Landeshauptstadt Dresden

The city of Dresden publishes realtime parking site data in the HTML page of its
[parking guidance system](https://www.dresden.de/apps_ext/ParkplatzApp/). Realtime data is scraped from this page.

Static data is not provided in a machine-readable format. It was converted from the former
[ParkAPI2-sources](https://github.com/ParkenDD/ParkAPI2-sources) GeoJSON and is made available as static GeoJSON at
[parkapi-static-data](https://github.com/ParkenDD/parkapi-static-data).


## Static values

* `purpose` is always `CAR`
* `has_realtime_data` is always `true`
* `uid` is the `id` query parameter of the detail page link, e.g. `431` for `./detail?id=431`
* bus parking sites have a restriction with type `BUS`
* parking sites without coordinates in the original data are not included
* `Stadtforum Dresden` (`468`) was added with coordinates from OpenStreetMap


## Realtime values

The page contains one `<table>` per area. Each `<tr>` in the `<tbody>` is one parking site.

* `realtime_data_updated_at` is set to the date in the `<div>` following the `<h3>Letzte Aktualisierung</h3>`
  headline, format `%d.%m.%Y %H:%M:%S`, timezone `Europe/Berlin`
* parking sites without free capacity value and without closed status are skipped, as they have no realtime data

| Field                        | Type           | Cardinality | Mapping                                           | Comment                                |
|------------------------------|----------------|-------------|---------------------------------------------------|----------------------------------------|
| `td[1] a[href]`              | string (url)   | 1           | uid                                               | `id` query parameter of the detail URL |
| `td[0][class]`               | string         | 1           | [realtime_opening_status](#RealtimeOpeningStatus) |                                        |
| `td[2] div.content`          | integer        | 1           | realtime_capacity                                 | Ignored if `0` or empty                |
| `td[3] div.content`          | integer        | ?           | realtime_free_capacity                            |                                        |


### RealtimeOpeningStatus

| Key                        | Mapping | Comment                                       |
|----------------------------|---------|-----------------------------------------------|
| class `park-closed`        | CLOSED  |                                               |
| any other class, with free | OPEN    | `green`, `yellow` or `red` icon               |
| any other class, no free   | -       | `blue` icon without data, dataset is skipped  |
