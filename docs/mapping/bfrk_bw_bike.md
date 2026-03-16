# BFRK BW Bike

BFRK BW Bike is a large JSON dataset with static `ParkingSite` data.

* `purpose` is set to `BIKE`
* `has_realtime_data` is set to `false`
* `static_data_updated_at` is set to now

A `ParkingSite` is generated if:
* `anlagentyp` is set
* `stellplatzanzahl` is set and `>= 1`


| Field                | Type                              | Cardinality | Mapping                            | Comment                                    |
|----------------------|-----------------------------------|-------------|------------------------------------|--------------------------------------------|
| infraid              | string                            | 1           | uid                                |                                            |
| lat                  | numeric                           | 1           | lat                                |                                            |
| lon                  | numeric                           | 1           | lon                                |                                            |
| anlagentyp           | [BfrkAnlagentyp](#BfrkAnlagentyp) | ?           | type, name, park_and_ride_type     |                                            |
| gemeinde             | string                            | ?           | address                            |                                            |
| ortsteil             | string                            | ?           | address += ` (`ortsteil`)`         | set only if ortsteil != gemeinde           |
| notiz                | string                            | ?           | description                        | set only if `!= "keine"`                   |
| objekt_Foto          | string (url)                      | ?           | photo_url                          |                                            |
| stellplatzanzahl     | integer                           | ?           | capacity                           |                                            |
| ueberdacht           | boolean                           | ?           | is_covered                         |                                            |
| beleuchtet           | boolean                           | ?           | has_lighting                       |                                            |
| kostenpflichtig      | boolean                           | ?           | has_fee                            |                                            |
| kostenpflichtignotiz | string                            | ?           | fee_description                    | set only if not starts with `keine Angabe` |
| hst_dhid             | string                            | 1           | external_identifiers[`DHID`].value |                                            |
| osmlinks             | string (url)                      | *           | external_identifiers[`OSM`].value  | one entry for each link                    |

### BfrkAnlagentyp
| Key                     | Mapping: type | Mapping: name       | Mapping: park_and_ride_type |
|-------------------------|---------------|---------------------|-----------------------------|
| Anlehnbuegel            | STANDS        | `Anlehnbügel`       |                             |
| Vorderradhalter         | WALL_LOOPS    | `Vorderradhalter`   |                             |
| Fahrradboxen            | LOCKERS       | `Fahrradboxen`      | [ParkAndRideType.YES]       |
| Fahrradsammelanlage     | SHED          | `Sammelanlage`      | [ParkAndRideType.YES]       |
| doppelstoeckig          | TWO_TIER      | `Zweistock-Anlage`  | [ParkAndRideType.YES]       |
| Fahrradparkhaus         | BUILDING      | `Fahrradparkhaus`   | [ParkAndRideType.YES]       |
| automatischesParksystem | BUILDING      | `Fahrradparkhaus`   | [ParkAndRideType.YES]       |
| Sonstiges               | FLOOR         | `Fahrradstellplatz` |                             |

