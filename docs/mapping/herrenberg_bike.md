# Stadt Herrenberg

Stadt Herrenberg provides static GeoJSON bike parking data on Munigrid platform.

* `purpose` is always `BIKE`
* `has_realtime_data` is always `false`

Static values:

The static data is provided over a GeoJSON API endpoint. 

| Source field/path                         | Type                                          | Cardinality | Target field             | Comment                                                                                                                        |
|-------------------------------------------|-----------------------------------------------|-------------|--------------------------|--------------------------------------------------------------------------------------------------------------------------------|
| geometry.coordinates                      | float                                         | 1           | lon/lat                  |                                                                                                                                |
| properties.fid                            | integer                                       | 1           | uid                      |                                                                                                                                |
| properties.Standortbeschreibung           | string                                        | 1           | name                     |                                                                                                                                |
| properties.Erfassungsdatum                | datetime                                      | 1           | static_data_updated_at   | Converted to this format`2025-04-29T06:56:45Z`                                                                                 |
| properties.Typ_Anlage                     | [ParkingSiteType](#ParkingSiteType)           | 1           | type                     |                                                                                                                                |
| properties.Davon_Ueberdacht               | [IsCovered](#IsCovered)                       | ?           | is_covered               |                                                                                                                                |
| properties.Anzahl_E_Ladepunkte            | [RestrictionsCharging](#RestrictionsCharging) | ?           | restrictions             | It is only mapped if the value `>= 1`                                                                                          |
| properties.Gebuehrenpflichtig             | [HasFee](#HasFee)                             | ?           | has_fee                  |                                                                                                                                |
| properties.Beleuchtet                     | [HasLightning](#HasLightning)                 | ?           | has_lighting             |                                                                                                                                |
| properties.SonstigeAnmerkungen            | string                                        | ?           | description              | It is only mapped if the value `!= ""`.                                                                                        |
| properties.OSM_ID                         | [ExternalIdentifiers](#ExternalIdentifiers)   | ?           | external_identifiers     | When the value is comma-separated string, each OSM ID is mapped to type `OSM` and listed in the `external_identifiers` array.  |


## ParkingSiteType

| Key                           | Mapping                                                        |
|-------------------------------|----------------------------------------------------------------|
| Bügel                         | `type` set to `STANDS`                                         |
| Reine Vorderradhalterung      | `type` set to `WALL_LOOPS`                                     |
| Bügel + Vorderradhalterung    | `type` set to `SAFE_WALL_LOOPS`                                |
| Fahrradboxen                  | `type` set to `LOCKERS`                                        |
| lean_and_stick                | `type` set to `STANDS`                                         |
| Holzkonstruktion              | `type` set to `SHED`                                           |
| Nische zum Abstellen          | `type` set to `FLOOR`                                          |
| Stange                        | `type` set to `STANDS`                                         |
| safe_loops                    | `type` set to `SAFE_WALL_LOOPS`                                |
| lockers                       | `type` set to `LOCKERS`                                        |


## IsCovered

| Key        | Mapping     |
|------------|-------------|
| >= 1       | true        |
| <= 0       | false       |


## HasFee

| Key        | Mapping     |
|------------|-------------|
| ja         | true        |
| nein       | false       |


## HasLightning

| Key        | Mapping     |
|------------|-------------|
| ja         | true        |
| nein       | false       |


## RestrictionsCharging

| Source field/path                 | Type        | Cardinality | Target field              | Comment                             |
|-----------------------------------|-------------|-------------|---------------------------|-------------------------------------|
| properties.Anzahl_E_Ladepunkte    | string      | ?           | restrictions.capacity     | Convert from string to integer      |
| properties.Anzahl_E_Ladepunkte    | string      | ?           | restrictions.type         | Set to `CHARGING`                   |


## ExternalIdentifiers

| Source field/path    | Type        | Cardinality | Target field                  | Comment            |
|----------------------|-------------|-------------|-------------------------------|--------------------|
| properties.OSM_ID    | string      | 1           | external_identifiers.value    |                    |
| properties.OSM_ID    | string      | 1           | external_identifiers.type     | Set to `OSM`       |
