# Freiburg VAG Bike

The Freiburger Verkehrs-AG publishes a GeoJSON dataset with locations of rentable bike lockers across the
city of Freiburg. Each feature describes a group of individual lockers that can be rented for storing
(cargo) bikes.

## `ParkingSite` Properties

Static values:

Each bike box is mapped to static `ParkingSite` as follows.
Attributes which are set statically by the converter:

* `type` is derived from the source and defaults to `LOCKERS`
* `has_realtime_data` is always set to `False`
* `opening_hours` is set to `24/7` when `durchg_geoeffnet` is `ja`

| Field               | Type     | Cardinality | Mapping                                            | Comment                                                                                                               |
|---------------------|----------|-------------|----------------------------------------------------|-----------------------------------------------------------------------------------------------------------------------|
| original_uid        | integer  | 1           | uid                                                |                                                                                                                       | 
| name                | string   | 1           | name                                               |                                                                                                                       |    
| purpose             | string   | 1           | [PurposeType](#PurposeType)                        |                                                                                                                       |
| capacity            | integer  | 1           | capacity                                           |                                                                                                                       |
| capacity_charging   | string   | 1           | [ParkingSiteRestriction](#ParkingSiteRestriction)  | Sets `capacity_charging` to `0` when value is `nein` and other values not integer are reported as validation error    |  
| max_heighth         | integer  | 1           | max_height                                         |                                                                                                                       |
| max_width           | integer  | 1           | max_width                                          |                                                                                                                       |
| is_covered          | string   | 1           | is_covered                                         | `ja` is set to `True`, `nein` is set to `False`                                                                       |
| related_location    | string   | 1           | related_location                                   | `ja` is set to `True`, `nein` is set to `False`                                                                       |
| has_fee             | string   | 1           | has_fee                                            | `ja` is set to `True`, `nein` is set to `False`                                                                       |
| fee_description     | string   | 1           | fee_description                                    |                                                                                                                       |
| durchg_geoeffnet    | string   | 1           | opening_hours                                      | `ja` is set to `24/7`, otherwise `None`                                                                               | 
| public_url          | string   | 1           | public_url                                         |                                                                                                                       |
| operator_name       | string   | 1           | operator_name                                      |                                                                                                                       |


## PurposeType

| Key        | Mapping      |
|------------|--------------|
| bike       | BIKE         |
| None       | ITEM         |


## ParkingSiteRestriction

| Key                     | Mapping                  |
|-------------------------|--------------------------|
| capacity_charging       | ParkingAudience.CHARGING |