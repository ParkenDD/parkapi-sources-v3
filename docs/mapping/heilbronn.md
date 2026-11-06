# Stadt Heilbronn

The city of Heilbronn publishes realtime parking site data of its parking guidance system as an
[HTML fragment](https://www.heilbronn.de/allgemeine-inhalte/ajax-parkhausbelegung?type=1496993343), which is
embedded at [heilbronn.de](https://www.heilbronn.de/umwelt-mobilitaet/mobilitaet/parken.html). Realtime data is
scraped from this fragment.

Static data is not provided in a machine-readable format. It was converted from the former
[ParkAPI2-sources](https://github.com/ParkenDD/ParkAPI2-sources) GeoJSON and is made available as static GeoJSON at
[parkapi-static-data](https://github.com/ParkenDD/parkapi-static-data).

Some parking sites are also part of other sources, e.g. `heilbronn_goldbeck`, `bb_parkhaus` or `apcoa`.


## Static values

* `purpose` is always `CAR`
* `has_realtime_data` is always `true`
* `uid` is the slugified name of the parking site, e.g. `kaethchenhof` for `Käthchenhof`
* `E-Quartiersgarage Neckarbogen` was added with coordinates and capacity from OpenStreetMap


## Realtime values

All parking sites are `<div class="carparkContent">` elements.

* `realtime_data_updated_at` is set to the first `<div class="col-sm-12">`, format
  `Datum: %d.%m.%Y - Uhrzeit: %H:%M:%S`, timezone `Europe/Berlin`
* `realtime_opening_status` is always `OPEN`
* parking sites without name or with `nicht fertiggestellt` in their name are skipped
* parking sites without free capacity value are skipped

| Field                              | Type    | Cardinality | Mapping                | Comment                                               |
|------------------------------------|---------|-------------|------------------------|-------------------------------------------------------|
| `div.carparkLocation` (first text) | string  | 1           | uid                    | slugified name, the following text is the access road |
| `div.col-sm-5`                     | integer | ?           | realtime_free_capacity | Text like `Freie Parkplätze: 195`                     |
