# Stadt Konstanz

Stadt Konstanz provides static GeoJSON bike parking data on their GIS platform.

- `purpose` is always `BIKE`
- `has_realtime_data` is always `false`

Static values:

The static data is provided over a GeoJSON API endpoint.

| Source field/path                       | Type                                          | Cardinality | Target field           | Comment                                                                 |
| --------------------------------------- | --------------------------------------------- | ----------- | ---------------------- | ------------------------------------------------------------------------|
| geometry.coordinates                    | float                                         | 1           | lon/lat                | Set midpoint of the Polygon as the coordinates                                                      |
| properties.OBJECTID                     | integer                                       | 1           | uid                    |                                                |
| properties.Lagebezeichnung              | string                                        | ?           | name                   | Set if the values are `!= null or != ""` else if no value use `Art`                                              |
| properties.Kapazitaet                   | int                                           | 1           | capacity               |                                                |
| properties.Art                          | [Art](#Art)                                   | 1           | type                   |                                                |
| properties.Ueberdachung                 | [Ueberdachung](#Ueberdachung)                 | ?           | is_covered             |                                                |
| properties.Eigentuemer_Baulasttraeger   | string                                        | ?           | operator_name          | Remove parking space entry If the value `== privat`                                                |
| properties.Beleuchtung                  | [Beleuchtung](#Beleuchtung)                   | ?           | has_lighting           |                                                |
| properties.Anmerkung                    | string                                        | ?           | description            | Set only if `!= null`                                               |
| properties.Stadtteil                    | string                                        | ?           | name                   | Set if available in addition to `Lagebezeichnung, Stadtteil` e.g. `Feuerwehr, Petershausen-West`  |

## Art

| Key                        | Mapping           |
| -------------------------- | ------------------|
| Anlehnbügel einseitig      | `STANDS`          |
| Anlehnbügel beidseitig     | `STANDS`          |
| Vorderradhalter            | `WALL_LOOPS`      |
| Vorderrad-Rahmenhalter     | `SAFE_WALL_LOOPS` |
| Markierte Fläche           | `FLOOR`           |
| Fahrradbox                 | `LOCKERS`         |

## Ueberdachung

| Key  | Mapping | Comment |
| ---- | ------- | ------- |
| 1    | true    | ja      |
| 0    | false   | nein    |

## Beleuchtung

| Key  | Mapping | Comment |
| ---- | ------- | ------- |
| 1    | true    | ja      |
| 0    | false   | nein    |
