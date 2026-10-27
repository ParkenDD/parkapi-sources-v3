# Landeshauptstadt Magdeburg

The ifak e.V. Magdeburg publishes realtime parking site data of the Magdeburg parking guidance system on the HTML page
[movi.de](https://www.movi.de/parkinfo/uebersicht.shtml). Realtime data is scraped from this page.

Static data is not provided in a machine-readable format. It was converted from the former
[ParkAPI2-sources](https://github.com/ParkenDD/ParkAPI2-sources) GeoJSON and is made available as static GeoJSON at
[parkapi-static-data](https://github.com/ParkenDD/parkapi-static-data).


## Static values

* `purpose` is always `CAR`
* `has_realtime_data` is always `true`
* `uid` is the file name of the detail page without extension, e.g. `park_mitte_alleecenter` for
  `http://www.movi.de/parkinfo/mitte/park_mitte_alleecenter.shtml`


## Realtime values

Parking sites are rows of the second inner `<table>` which contain a link and at least five cells. The first row of each
area has an additional first cell with the area name, so all following cells are shifted by one.

* `realtime_opening_status` is always `OPEN`
* parking sites without valid date are skipped, as the source shows `Es stehen keine Online-Daten zur Verfügung`
  instead
* parking sites without free capacity value are skipped, e.g. `offline`

| Field         | Type              | Cardinality | Mapping                  | Comment                                                         |
|---------------|-------------------|-------------|--------------------------|-----------------------------------------------------------------|
| `td[0] a`     | string (url)      | 1           | uid                      | file name of the detail URL without `.shtml`                    |
| `td[1]`       | integer           | 1           | realtime_free_capacity   |                                                                 |
| `td[4]`       | string (datetime) | 1           | realtime_data_updated_at | format `%d.%m.%Y %H:%M Uhr`, timezone `Europe/Berlin`           |
