# Stadt Hanau

The city of Hanau publishes realtime parking site data on the HTML page [parken-hanau.de](https://parken-hanau.de/).
Realtime data is scraped from this page.

Static data is not provided in a machine-readable format. It was converted from the former
[ParkAPI2-sources](https://github.com/ParkenDD/ParkAPI2-sources) GeoJSON and is made available as static GeoJSON at
[parkapi-static-data](https://github.com/ParkenDD/parkapi-static-data).


## Static values

* `purpose` is always `CAR`
* `has_realtime_data` is always `true`
* `uid` is the slugified name of the parking site, e.g. `parkhaus-nuernberger-strasse` for
  `Parkhaus Nuernberger Strasse`. Umlauts are transliterated, so `ü` and `ue` result in the same `uid`.
* `Parkhaus Klinikum` was added with coordinates from OpenStreetMap


## Realtime values

All parking sites are `<div class="well">` elements in the `<div class="container-fluid">`.

* `realtime_data_updated_at` is set to the `<h5>` in the container, format
  `Letzte Aktualisierung: %d.%m.%Y %H:%M:%S`, timezone `Europe/Berlin`
* `realtime_opening_status` is always `OPEN`
* parking sites without free capacity value are skipped
* parking sites with capacity `0` and free capacity `0` are skipped, as they are offline

| Field                                | Type    | Cardinality | Mapping                | Comment                                        |
|--------------------------------------|---------|-------------|------------------------|------------------------------------------------|
| `b`                                  | string  | 1           | uid                    | slugified name                                 |
| `span.badge`                         | integer | ?           | realtime_capacity      | Text like `170 Plätze`                         |
| `div[role=progressbar]` (second) `b` | integer | 1           | realtime_free_capacity | Second progress bar contains the free capacity |
