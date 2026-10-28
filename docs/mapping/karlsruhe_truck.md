# TechnologieRegion Karlsruhe: LKW-Parkplätze

The TechnologieRegion Karlsruhe publishes its truck parking sites as GeoJSON with Point geometries at the layer
`TBA:lkw_parken` of its [GeoServer](https://mobil.trk.de/geoserver/TBA/ows). The layer is published at the
Mobilithek by Digitale Mobilität ([offer](https://mobilithek.info/offers/-953782865562856186)). Each feature becomes a
`ParkingSite`. There is no realtime data.

Features without `stellplaetze` or with `stellplaetze` `0` are ignored. If the config key
`PARK_API_KARLSRUHE_TRUCK_IGNORE_MISSING_CAPACITIES` is set to `false`, features without `stellplaetze` are reported as
validation errors instead, and features with `0` are imported.

Static values:

* `purpose` is always `CAR`
* `type` is always `OTHER`
* `has_realtime_data` is always `false`
* `restrictions` always contains one restriction with `type` `TRUCK` and the full capacity
* `lat` / `lon` are taken from the Point geometry, rounded to 7 decimal places
* text fields have non-breaking spaces replaced by spaces, line breaks by spaces and carriage returns removed

## Static data

| Field         | Type               | Cardinality | Mapping                            | Comment                                            |
|---------------|--------------------|-------------|------------------------------------|----------------------------------------------------|
| id            | integer            | 1           | uid                                |                                                    |
| gemeinde      | string             | 1           | address                            | `address` is `{standort}, {stadtteil}, {gemeinde}` |
| stadtteil     | string             | ?           | address                            |                                                    |
| standort      | string             | 1           | name, address                      |                                                    |
| gebuehren     | string             | ?           | has_fee, fee_description           | see [Fees](#Fees)                                  |
| parkzeit      | string             | ?           |                                    | free text, not used                                |
| max_parkdauer | string             | ?           |                                    | free text, not used                                |
| stellplaetze  | integer            | 1           | capacity, restrictions[0].capacity | ignored per default if missing or `0`              |
| bemerkung     | string             | ?           | description                        |                                                    |
| stand         | string (date-time) | 1           | static_data_updated_at             |                                                    |

### Fees

| Value                               | Mapping                                       |
|-------------------------------------|-----------------------------------------------|
| `frei` or `gebührenfrei` (any case) | `has_fee` is `false`                          |
| any other value                     | `has_fee` is `true`, `fee_description` is set |
| missing                             | `has_fee` is not set                          |
