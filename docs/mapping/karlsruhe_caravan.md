# TechnologieRegion Karlsruhe: Wohnmobilparkplätze

The TechnologieRegion Karlsruhe publishes its caravan parking sites as GeoJSON with Point geometries at the layer
`TBA:wohnmobil_parken` of its [GeoServer](https://mobil.trk.de/geoserver/TBA/ows). The layer is published at the
Mobilithek by Digitale Mobilität ([offer](https://mobilithek.info/offers/-7891685249328848425)). Each feature becomes a
`ParkingSite`. There is no realtime data.

Features without `stellplaetze` or with `stellplaetze` `0` are ignored. If the config key
`PARK_API_KARLSRUHE_CARAVAN_IGNORE_MISSING_CAPACITIES` is set to `false`, features without `stellplaetze` are reported
as validation errors instead, and features with `0` are imported.

Static values:

* `purpose` is always `CAR`
* `type` is always `OTHER`
* `has_realtime_data` is always `false`
* `restrictions` always contains one restriction with `type` `CARAVAN` and the full capacity
* `lat` / `lon` are taken from the Point geometry, rounded to 7 decimal places
* text fields have non-breaking spaces replaced by spaces, line breaks by spaces and carriage returns removed

## Static data

| Field          | Type               | Cardinality | Mapping                            | Comment                                                 |
|----------------|--------------------|-------------|------------------------------------|---------------------------------------------------------|
| id             | integer            | 1           | uid                                |                                                         |
| gemeinde       | string             | 1           | address                            | `address` is `{standort}, {stadtteil}, {gemeinde}`      |
| stadtteil      | string             | ?           | address                            |                                                         |
| standort       | string             | 1           | name, address                      |                                                         |
| gebuehren      | string             | ?           | has_fee, fee_description           | see [Fees](#Fees)                                       |
| parkzeit       | string             | ?           |                                    | free text, not used                                     |
| max_parkdauer  | string             | ?           |                                    | free text, not used                                     |
| stellplaetze   | integer            | ?           | capacity, restrictions[0].capacity | ignored per default if missing or `0`                   |
| akzept_muenzen | string             | ?           |                                    | accepted coins, e.g. `0,10/0,20/0,50/1/2 Euro`          |
| geldkarte      | string             | ?           |                                    | `T` or `F`                                              |
| fremdsprache   | string             | ?           |                                    | `T` or `F`                                              |
| frischwasser   | string             | ?           |                                    | fresh water, `F` or a price description                 |
| strom          | string             | ?           |                                    | electricity, a price description                        |
| entsorgung     | string             | ?           |                                    | `T` or `F`                                              |
| kurtaxepflicht | string             | ?           |                                    | `T` or `F`                                              |
| nachtruhe      | string             | ?           |                                    | e.g. `22 - 6 Uhr`                                       |
| bemerkung      | string             | ?           | description                        |                                                         |
| stand          | string (date-time) | 1           | static_data_updated_at             |                                                         |

### Fees

| Value                               | Mapping                                       |
|-------------------------------------|-----------------------------------------------|
| `frei` or `gebührenfrei` (any case) | `has_fee` is `false`                          |
| any other value                     | `has_fee` is `true`, `fee_description` is set |
| missing                             | `has_fee` is not set                          |
