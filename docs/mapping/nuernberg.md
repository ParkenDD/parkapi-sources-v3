# Stadt Nürnberg

The city of Nürnberg publishes realtime parking site data on the HTML page of its
[Tiefbauamt](https://tiefbauamt.nuernberg.de/site/parken/parkhausbelegung/parkhaus_belegung.html). Realtime data is
scraped from this page.

Static data is not provided in a machine-readable format. It was converted from the former
[ParkAPI2-sources](https://github.com/ParkenDD/ParkAPI2-sources) GeoJSON and is made available as static GeoJSON at
[parkapi-static-data](https://github.com/ParkenDD/parkapi-static-data).


## Static values

* `purpose` is always `CAR`
* `has_realtime_data` is always `true`
* `uid` is the slugified name of the parking site, e.g. `parkhaus-sebalder-hoefe` for `Parkhaus Sebalder Höfe`


## Realtime values

Each parking site is a `<tr>` with its name in a `<p class="bold">`.

* `realtime_data_updated_at` is set to the `<td width="233">`, format `Stand vom %d.%m.%Y, %H:%M:%S`, timezone
  `Europe/Berlin`
* `realtime_opening_status` is always `OPEN`
* parking sites without free capacity value are skipped

| Field   | Type    | Cardinality | Mapping                | Comment                                                         |
|---------|---------|-------------|------------------------|-----------------------------------------------------------------|
| `td[1]` | string  | 1           | uid                    | slugified name, line breaks and indentation are normalized      |
| `td[2]` | integer | 1           | realtime_free_capacity |                                                                 |
| `td[3]` | integer | ?           | realtime_capacity      |                                                                 |
