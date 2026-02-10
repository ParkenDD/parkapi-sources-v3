# BFRK BW Car

BFRK BW Car is a large JSON dataset with static `ParkingSite` and `ParkingSpot` data.

* `purpose` is set to `CAR`
* `has_realtime_data` is set to `false`
* `static_data_updated_at` is set to now

A `ParkingSite` is generated if:
* `oeffentlichvorhanden` is not set or `== true`
* `stellplaetzegesamt` is set and `>= 1`

One or more `ParkingSpot`s are generated if:
* `oeffentlichvorhanden` is not set or `== true`
* `behindertenstellplaetze` is set and `>= 1`
* `behindertenplaetze_lat` and `behindertenplaetze_lon` are set

`ParkingSpot`s obtain a `parking_site_id` to reference their `ParkingSite`, if existing.

Multiple `ParkingSpot`s are distributed a bit from each other.


| Field                   | Type                          | Cardinality | Mapping `ParkingSite`              | Mapping `ParkingSpot`              | Comment                                                 |
|-------------------------|-------------------------------|-------------|------------------------------------|------------------------------------|---------------------------------------------------------|
| infraid                 | string                        | 1           | uid                                | uid                                |                                                         |
| lat                     | numeric                       | 1           | lat                                |                                    |                                                         |
| lon                     | numeric                       | 1           | lon                                |                                    |                                                         |
| bauart                  | [BfrkBauart](#BfrkBauart)     | ?           | type, name                         | type, name                         | defined by 25% of all sites                             |
| art                     | [BfrkArt](#BfrkArt)           | ?           | type, name, park_and_ride_type     | type, name, park_and_ride_type     | set type, name only if not set by bauart                |
| gemeinde                | string                        | ?           | address                            | address                            |                                                         |
| ortsteil                | string                        | ?           | address += ` (`ortsteil`)`         | address += ` (`ortsteil`)`         | set only if ortsteil != gemeinde                        |
| eigentuemer             | string                        | ?           | operator_name                      | operator_name                      | set only if `!= ""`                                     |
| bedingungen             | string                        | ?           | description                        | description                        | set only if `!= "keine"|"keine Angabe"|"keine Angaben"` |
| objekt_Foto             | string (url)                  | ?           | photo_url                          |                                    | set only if `!= ""`                                     |
| stellplaetzegesamt      | integer                       | ?           | capacity                           |                                    |                                                         |
| frauenstellplaetze      | integer                       | ?           | restrictions[`WOMAN`].capacity     |                                    | set only if `>= 1`                                      |
| familienstellplaetze    | integer                       | ?           | restrictions[`FAMILY`].capacity    |                                    | set only if `>= 1`                                      |
| behindertenstellplaetze | integer                       | ?           | restrictions[`DISABLED`].capacity  | restrictions[`DISABLED`]           | set only if `>= 1`                                      |
| behindertenplaetze_lat  | numeric                       | ?           |                                    | lat                                |                                                         |
| behindertenplaetze_lon  | numeric                       | ?           |                                    | lon                                |                                                         |
| behindertenplaetze_Foto | string (url)                  | ?           |                                    | photo_url                          | set only if `!= ""`                                     |
| orientierung            | [Orientierung](#Orientierung) | ?           | orientation                        |                                    |                                                         |
| oeffnungszeiten         | string                        | ?           | opening_hours                      | opening_hours                      |                                                         |
| offen_24_7              | boolean                       | ?           | opening_hours = `24/7`             | opening_hours = `24/7`             | set if true and oeffnungszeiten is not set              |
| maxparkdauer_min        | integer                       | ?           | restrictions.max_stay              | restrictions.max_stay              | set if `!= -1`, map to ISO 8601 duration format         |
| gebuehrenpflichtig      | string                        | ?           | has_fee                            |                                    | set true if `== "ja"`, set false if `== "nein"`         |
| gebuehrenbeispiele      | string                        | ?           | fee_description                    |                                    |                                                         |
| hst_dhid                | string                        | 1           | external_identifiers[`DHID`].value | external_identifiers[`DHID`].value |                                                         |
| osmlinks                | string (url)                  | *           | external_identifiers[`OSM`].value  | external_identifiers[`OSM`].value  | one entry for each link                                 |

### BfrkBauart
| Key                      | Mapping: type             | Mapping: name       |
|--------------------------|---------------------------|---------------------|
| parkhaus_hoch            | CAR_PARK                  | `Parkhaus`          |
| parkhaus_tief            | UNDERGROUND               | `Tiefgarage`        |
| parkplatz                | OFF_STREET_PARKING_GROUND | `Parkplatz`         |
| strasse_parkbucht        | OFF_STREET_PARKING_GROUND | `Parkplatz`         |
| auf_strasse              | ON_STREET                 | `Straßen-Parkplatz` |

### BfrkArt
| Key                      | Mapping: type             | Mapping: name | Mapping: park_and_ride_type |
|--------------------------|---------------------------|---------------|-----------------------------|
| Parkhaus                 | CAR_PARK                  | `Parkhaus`    |                             |
| Park+Ride                | OFF_STREET_PARKING_GROUND | `Parkplatz`   | [ParkAndRideType.YES]       |
| Parkplatz_ohne_Park+Ride | OFF_STREET_PARKING_GROUND | `Parkplatz`   |                             |
| Kurzzeit                 | OFF_STREET_PARKING_GROUND | `Parkplatz`   |                             |
| Behindertenplätze        | OFF_STREET_PARKING_GROUND | `Parkplatz`   |                             |

### Orientierung
| Key                      | Mapping       |
|--------------------------|---------------|
| laengs                   | PARALLEL      |
| quer                     | PERPENDICULAR |
| diagonal                 | DIAGONAL      |

