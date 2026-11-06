# Stadt Herrenberg

Stadt Herrenberg provides static GeoJSON bike parking data on Munigrid platform.

- `purpose` is always `BIKE`
- `has_realtime_data` is always `false`

Datasets without `Anzahl_Abstellmoeglichkeiten` are ignored silently. If the config key
`PARK_API_HERRENBERG_BIKE_IGNORE_MISSING_CAPACITIES` is set to `false`, they are reported as validation errors instead.

Datasets without `Typ_Anlage` are reported as validation errors. If the config key
`PARK_API_HERRENBERG_BIKE_IGNORE_MISSING_TYPES` is set to `true`, they are ignored silently instead.

Static values:

The static data is provided over a GeoJSON API endpoint.

| Source field/path                       | Type                                          | Cardinality | Target field           | Comment                                                                                                                       |
| --------------------------------------- | --------------------------------------------- | ----------- | ---------------------- | ----------------------------------------------------------------------------------------------------------------------------- |
| geometry                                | Point or Polygon                              | 1           | lon/lat, geojson       | For polygons, the centroid is used as lon/lat, and the polygon is set as `geojson`.                                           |
| properties.fid                          | integer                                       | 1           | uid                    |                                                                                                                               |
| properties.Standortbeschreibung         | string                                        | 1           | name                   |                                                                                                                               |
| properties.Erfassungsdatum              | date                                          | 1           | static_data_updated_at | Converted to this format`2025-04-29T06:56:45Z`                                                                                |
| properties.Anzahl_Abstellmoeglichkeiten | int                                           | 1           | capacity               |                                                                                                                               |
| properties.Typ_Anlage                   | [ParkingSiteType](#parkingsitetype)           | 1           | type                   | Leading and trailing whitespace is ignored.                                                                                   |
| properties.Davon_Ueberdacht             | [IsCovered](#iscovered)                       | ?           | is_covered             |                                                                                                                               |
| properties.Anzahl_E_Ladepunkte          | [RestrictionsCharging](#restrictionscharging) | ?           | restrictions           | It is only mapped if the value `>= 1`                                                                                         |
| properties.Gebuehrenpflichtig           | [HasFee](#hasfee)                             | ?           | has_fee                |                                                                                                                               |
| properties.Beleuchtet                   | [HasLightning](#haslightning)                 | ?           | has_lighting           |                                                                                                                               |
| properties.SonstigeAnmerkungen          | string                                        | ?           | description            | It is only mapped if the value `!= ""`.                                                                                       |
| properties.OSM_ID                       | [ExternalIdentifiers](#externalidentifiers)   | ?           | external_identifiers   | When the value is comma-separated string, each OSM ID is mapped to type `OSM` and listed in the `external_identifiers` array. |

## ParkingSiteType

| Key                        | Mapping                         |
| -------------------------- | ------------------------------- |
| Bügel                      | `type` set to `STANDS`          |
| Reine Vorderradhalterung   | `type` set to `WALL_LOOPS`      |
| Bügel + Vorderradhalterung | `type` set to `SAFE_WALL_LOOPS` |
| Schließfächer/ Boxen       | `type` set to `LOCKERS`         |
| andere                     | `type` set to `FLOOR`           |

## IsCovered

| Key  | Mapping |
| ---- | ------- |
| >= 1 | true    |
| <= 0 | false   |

## HasFee

| Key  | Mapping |
| ---- | ------- |
| ja   | true    |
| nein | false   |

## HasLightning

| Key  | Mapping |
| ---- | ------- |
| ja   | true    |
| nein | false   |
| ""   | ???     |

## RestrictionsCharging

| Source field/path              | Type   | Cardinality | Target field          | Comment                        |
| ------------------------------ | ------ | ----------- | --------------------- | ------------------------------ |
| properties.Anzahl_E_Ladepunkte | string | ?           | restrictions.capacity | Convert from string to integer |
| properties.Anzahl_E_Ladepunkte | string | ?           | restrictions.type     | Set to `CHARGING`              |

## ExternalIdentifiers

| Source field/path | Type   | Cardinality | Target field               | Comment      |
| ----------------- | ------ | ----------- | -------------------------- | ------------ |
| properties.OSM_ID | string | 1           | external_identifiers.value |              |
| properties.OSM_ID | string | 1           | external_identifiers.type  | Set to `OSM` |
