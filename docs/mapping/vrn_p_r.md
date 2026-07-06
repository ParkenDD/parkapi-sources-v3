# Realtime and Static P+R data of Verkehrsverbund Rhein-Neckar (VRN)

The Verkehrsverbund Rhein-Neckar GmbH provides `GeoJSON` data for Park + Ride parking sites equipped with VRN parking
sensors. The data is fetched from the VRN spatial `FeatureServer` and contains both static information and current
occupancy for cars. Each `feature` consists of a `Point` geometry and a `properties` object and is mapped to a
`ParkingSite`.

Static values:

* `purpose` is always `CAR`

Ignore rules:

* If the config key `PARK_API_VRN_P_R_IGNORE_MISSING_CAPACITIES` is set, features without a `capacity` are ignored.
* Realtime data is only generated for features that provide a `realtime_free_capacity`.

## geometry

| Field         | Type    | Cardinality | Mapping | Comment                        |
|---------------|---------|-------------|---------|--------------------------------|
| @type         | enum    | 1           |         | always `Point`                 |
| coordinates.1 | numeric | 1           | lat     | latitude, rounded to 7 digits  |
| coordinates.0 | numeric | 1           | lon     | longitude, rounded to 7 digits |

## properties – Static ParkingSites

The `uid` is assembled from `original_uid` and `vrn_sensor_id` as `{original_uid}-{vrn_sensor_id}`.

| Field                 | Type     | Cardinality | Mapping                                     | Comment                                                                                 |
|-----------------------|----------|-------------|---------------------------------------------|-----------------------------------------------------------------------------------------|
| original_uid          | string   | 1           | uid                                         | combined with `vrn_sensor_id`                                                           |
| vrn_sensor_id         | integer  | ?           | uid                                         | combined with `original_uid`                                                            |
| name                  | string   | 1           | name                                        | empty strings are replaced by `P+R Parkplätze`                                          |
| type                  | enum     | ?           | [type](#VrnParkAndRideType)                 |                                                                                         |
| public_url            | string   | ?           | public_url                                  |                                                                                         |
| photo_url             | string   | ?           | photo_url                                   |                                                                                         |
| lat                   | numeric  | 1           |                                             | present in properties, but `lat` is taken from the geometry                             |
| lon                   | numeric  | 1           |                                             | present in properties, but `lon` is taken from the geometry                             |
| address               | string   | ?           |                                             | not used                                                                                |
| operator_name         | string   | ?           | operator_name                               |                                                                                         |
| capacity              | integer  | 1           | capacity                                    | feature ignored if missing when `PARK_API_VRN_P_R_IGNORE_MISSING_CAPACITIES` set        |
| capacity_charging     | integer  | ?           | restrictions[].capacity                     | restriction type [`CHARGING`](#ParkingAudience)                                         |
| capacity_family       | integer  | ?           | restrictions[].capacity                     | restriction type [`FAMILY`](#ParkingAudience)                                           |
| capacity_woman        | integer  | ?           | restrictions[].capacity                     | restriction type [`WOMEN`](#ParkingAudience)                                            |
| capacity_bus          | integer  | ?           | restrictions[].capacity                     | restriction type [`BUS`](#ParkingAudience)                                              |
| capacity_truck        | integer  | ?           | restrictions[].capacity                     | restriction type [`TRUCK`](#ParkingAudience)                                            |
| capacity_carsharing   | integer  | ?           | restrictions[].capacity                     | restriction type [`CHARGING`](#ParkingAudience)                                         |
| capacity_disabled     | integer  | ?           | restrictions[].capacity                     | restriction type [`DISABLED`](#ParkingAudience)                                         |
| max_height            | integer  | ?           | max_height                                  |                                                                                         |
| has_realtime_data     | boolean  | ?           | has_realtime_data                           | mapped from `ja`/`nein`, defaults to `False`                                            |
| has_lighting          | boolean  | ?           | has_lighting                                | mapped from `ja`/`nein`                                                                 |
| has_fee               | boolean  | ?           | has_fee                                     | mapped from `ja`/`nein`                                                                 |
| is_covered            | boolean  | ?           | is_covered                                  | mapped from `ja`/`nein`                                                                 |
| related_location      | string   | ?           | related_location                            |                                                                                         |
| opening_hours         | string   | ?           | opening_hours                               | set to `24/7` if it contains `Mo-So: 24 Stunden` or `Mo-So: Kostenlos`, otherwise unset |
| park_and_ride_type    | enum     | ?           | [park_and_ride_type](#VrnParkAndRidePRType) | wrapped in a single-element list                                                        |
| max_stay              | integer  | ?           | max_stay, restrictions[].max_stay           | seconds; also applied to every restriction                                              |
| fee_description       | string   | ?           | fee_description                             |                                                                                         |
| realtime_data_updated | datetime | ?           | static_data_updated_at                      | unix timestamp in ms; defaults to import time if absent                                 |

## properties – Realtime ParkingSites

Realtime data is only generated when `realtime_free_capacity` is present.

| Field                   | Type     | Cardinality | Mapping                                                           | Comment                                                                      |
|-------------------------|----------|-------------|-------------------------------------------------------------------|------------------------------------------------------------------------------|
| original_uid            | string   | 1           | uid                                                               | combined with `vrn_sensor_id`                                                |
| vrn_sensor_id           | integer  | ?           | uid                                                               | combined with `original_uid`                                                 |
| realtime_free_capacity  | integer  | ?           | realtime_free_capacity                                            | realtime data is skipped entirely if missing                                 |
| realtime_occupied       | integer  | ?           | realtime_capacity                                                 | `realtime_capacity = realtime_free_capacity + realtime_occupied` if both set |
| realtime_opening_status | enum     | ?           | [realtime_opening_status](#VrnParkAndRidePropertiesOpeningStatus) |                                                                              |
| realtime_data_updated   | datetime | ?           | realtime_data_updated_at                                          | unix timestamp in ms; defaults to import time if absent                      |

## Enumerations

### VrnParkAndRideType

Mapped to `type`.

| Key       | Mapping                   |
|-----------|---------------------------|
| Parkhaus  | CAR_PARK                  |
| Parkplatz | OFF_STREET_PARKING_GROUND |

### VrnParkAndRidePRType

Mapped to `park_and_ride_type`. Any other or missing value falls back to `NO`.

| Key  | Mapping |
|------|---------|
| ja   | YES     |
| nein | NO      |

### VrnParkAndRidePropertiesOpeningStatus

Mapped to `realtime_opening_status`.

| Key       | Mapping |
|-----------|---------|
| unbekannt | UNKNOWN |

### ParkingAudience

Used as the restriction `type` for the various capacity fields.

| Key        | Comment                  |
|------------|--------------------------|
| DISABLED   | from `capacity_disabled` |
| WOMEN      | from `capacity_woman`    |
| FAMILY     | from `capacity_family`   |
| BUS        | from `capacity_bus`      |
| TRUCK      | from `capacity_truck`    |
| CARSHARING | from `capacity_charging` |
| CHARGING   | from `capacity_charging` |
