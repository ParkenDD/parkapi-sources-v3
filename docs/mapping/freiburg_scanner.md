# Freiburg Scanner

Freiburg Scanner is a large dataset with scan car data.

Attributes which are set statically:

* `has_realtime_data` is always set to `False`
* `type` is always set to `ON_STREET`
* `purpose` is always set to `CAR`
* `static_data_updated_at` is set to the moment of the import


| Field                 | Type    | Cardinality | Mapping                    | Comment                                                                          |
|-----------------------|---------|-------------|----------------------------|----------------------------------------------------------------------------------|
| id                    | string  | 1           | uid                        |                                                                                  |
| capacity              | integer | 1           | capacity                   | Datasets with capacity 0 are ignored                                             |
| confidence_interval   | string  | 1           | capacity_min, capacity_max | Format is `{i,j}`, where i is capacity_min and j is capacity_max, both integers. |
| is_narrow             | integer | 1           |                            |                                                                                  |
| kr_strassenschluessel | string  | 1           |                            |                                                                                  |
| kr_strassenname       | string  | 1           | name, address              | address is set to `{kr_strassenname}, Freiburg`                                  |
