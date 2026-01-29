# Stadt Herrenberg

Stadt Herrenberg provides static bike parking data on Munigrid platform.

* `purpose` is always `BIKE`
* `has_realtime_data` is always `False`

Static values:

The static data is provided over a GeoJSON endpoint. 

| Source field/path                         | Type                                          | Cardinality | Target field             | Comment                                         |
|-------------------------------------------|-----------------------------------------------|-------------|--------------------------|-------------------------------------------------|
| properties.fid                            | integer                                       | 1           | uid                      |                                                 |
| properties.Standortbeschreibung           | string                                        | 1           | name                     |                                                 |
| properties.Erfassungsdatum                | datetime                                      | 1           | static_data_updated_at   | Converted to this format`2025-04-29T06:56:45Z`  |
| geometry.coordinates                      | float                                         | 1           | lat                      |                                                 |
| geometry.coordinates                      | float                                         | 1           | lon                      |                                                 |
| properties.Typ_Anlage                     | [ParkingSiteType](#ParkingSiteType)           | 1           | type                     |                                                 |
| properties.Davon_Ueberdacht               | [IsCovered](#IsCovered)                       | ?           | is_covered               |                                                 |
| properties.Anzahl_E_Ladepunkte            | [RestrictionsCharging](#RestrictionsCharging) | ?           | restrictions             |                                                 |
| properties.Gebuehrenpflichtig             | [HasFee](#HasFee)                             | ?           | has_fee                  |                                                 |
| properties.Beleuchtet                     | [HasLightning](#HasLightning)                 | ?           | has_lighting             |                                                 |
| properties.SonstigeAnmerkungen            | string                                        | ?           | description              |                                                 |


## ParkingSiteType

| Key                           | Mapping                                                        |
|-------------------------------|----------------------------------------------------------------|
| Bügel                         | `type` set to `STANDS`                                         |
| Reine Vorderradhalterung      | `type` set to `WALL_LOOPS`                                     |
| Bügel + Vorderradhalterung    | `type` set to `WALL_LOOPS`                                     |
| Fahrradboxen                  | `type` set to `LOCKERS`, `park_and_ride_type` set to `YES`     |
| lean_and_stick                | `type` set to `STANDS`                                         |
| Holzkonstruktion              | `type` set to `CAR_PARK`                                       |
| Nische zum Abstellen          | `type` set to `SHED`                                           |
| Stange                        | `type` set to `STANDS`                                         |
| safe_loops                    | `type` set to `SAFE_WALL_LOOPS`                                |
| lockers                       | `type` set to `LOCKERS`                                        |


## IsCovered

| Key        | Mapping     |
|------------|-------------|
| > 0        | True        |
| <= 0       | False       |


## HasFee

| Key        | Mapping     |
|------------|-------------|
| ja         | True        |
| nein       | False       |


## HasLightning

| Key        | Mapping     |
|------------|-------------|
| ja         | True        |
| nein       | False       |


## RestrictionsCharging

| Source field/path                 | Type        | Cardinality | Target field              | Comment                             |
|-----------------------------------|-------------|-------------|---------------------------|-------------------------------------|
| properties.Anzahl_E_Ladepunkte    | string      | ?           | restrictions.capacity     | Convert from string to integer      |
| properties.Anzahl_E_Ladepunkte    | string      | ?           | restrictions.type         | Set to `CHARGING`                   |
