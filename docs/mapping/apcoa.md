# APCOA-SERVICES

APCOA provides a JSON REST API (`/carpark/v4/Carparks`) with static parking site data across many countries. Access
requires an API subscription key (`PARK_API_APCOA_API_SUBSCRIPTION_KEY`). The response contains a `Results` list, where
each entry is one parking site. Although the API models realtime data, it is not called yet, so only static data is
imported.

Ignored entries:

* Park & Control objects (`SiteIdLong` starts with `S1180_` and `ShowAs` is `SURVEILLANCE_OBJECT`) are skipped, as they
  are not allowed to be published
* entries with `ShowAs` equal to `HIDDEN` are skipped
* if `PARK_API_APCOA_IGNORE_MISSING_COORDINATES` is set, entries without `NavigationLocations` are skipped
* entries without a `Total Spaces` capacity in `Spaces` raise a validation error and are skipped
* entries with a negative `Count` for any space type other than `Urban Hubs reserved` raise a validation error and are
  skipped

Static values:

* `purpose` is always `CAR`
* `has_realtime_data` is always `False` (the API does not offer realtime data yet)

| Field                | Type                                                | Cardinality | Mapping                | Comment                                                                    |
|----------------------|-----------------------------------------------------|-------------|------------------------|----------------------------------------------------------------------------|
| CarParkId            | integer                                             | 1           | uid                    |                                                                            |
| CarparkLongName      | string                                              | ?           | name                   | falls back to `CarparkShortName` if empty                                  |
| CarparkShortName     | string                                              | ?           | name                   | used as `name` if `CarparkLongName` is empty                               |
| CarParkWebsiteURL    | string                                              | ?           | public_url             |                                                                            |
| CarParkPhotoURLs     | [CarParkPhotoURLs](#CarParkPhotoURLs)               | ?           | photo_url              | `CarparkPhotoURL1` is used as `photo_url`                                  |
| CarparkType          | [CarparkType](#CarparkType)                         | 1           | type                   | `Name` maps to `type`; `None` results in no `type`                         |
| Address              | [Address](#Address)                                 | 1           | address                | only assembled if `Street`, `Zip` and `City` are all set                   |
| NavigationLocations  | list of [NavigationLocations](#NavigationLocations) | +           | lat, lon               | the entry with `LocationType` = `default` provides the coordinates         |
| Spaces               | list of [Spaces](#Spaces)                           | +           | capacity, restrictions | `Total Spaces` maps to `capacity`, other types map to `restrictions`       |
| OpeningHours         | list of [OpeningHours](#OpeningHours)               | *           | opening_hours          | converted to OSM opening hours format                                      |
| LastModifiedDateTime | datetime                                            | 1           | static_data_updated_at | space-separated datetime, local timezone `Europe/Berlin`, converted to UTC |
| IndicativeTariff     | [IndicativeTariff](#IndicativeTariff)               | ?           | has_fee                | `has_fee` is set to `True` if `MinValue` or `MaxValue` is set              |

### CarParkPhotoURLs

Only `CarparkPhotoURL1` is used (as `photo_url`). The remaining URLs are validated but ignored.

| Field            | Type   | Cardinality | Mapping   | Comment |
|------------------|--------|-------------|-----------|---------|
| CarparkPhotoURL1 | string | ?           | photo_url |         |
| CarparkPhotoURL2 | string | ?           |           |         |
| CarparkPhotoURL3 | string | ?           |           |         |
| CarparkPhotoURL4 | string | ?           |           |         |

### Address

Assembled into `address` as `{Street}, {Zip} {City}`, but only if `Street`, `Zip` and `City` are all set.

| Field  | Type   | Cardinality | Mapping | Comment    |
|--------|--------|-------------|---------|------------|
| Street | string | ?           | address |            |
| Zip    | string | ?           | address |            |
| City   | string | ?           | address |            |
| Region | string | ?           |         | not used   |

### NavigationLocations

Provides the coordinates. The first entry with `LocationType` = `default` is used for `lat` / `lon`.

| Field                    | Type    | Cardinality | Mapping | Comment                                                                          |
|--------------------------|---------|-------------|---------|----------------------------------------------------------------------------------|
| GeoCoordinates.Latitude  | numeric | 1           | lat     |                                                                                  |
| GeoCoordinates.Longitude | numeric | 1           | lon     |                                                                                  |
| LocationType             | string  | ?           |         | `default` entry provides the coordinates; other values (e.g. `CarEntry`) ignored |

### Spaces

Each entry is one capacity per space type. The `Total Spaces` entry provides the overall `capacity`; other recognized
types are added as `restrictions` with the mapped `ParkingAudience` and their `Count`. See [SpaceType](#SpaceType) for
the mapping. Unrecognized types are ignored.

| Field | Type                    | Cardinality | Mapping                | Comment                     |
|-------|-------------------------|-------------|------------------------|-----------------------------|
| Type  | [SpaceType](#SpaceType) | 1           | capacity, restrictions |                             |
| Count | integer                 | 1           | capacity, restrictions | may be a string             |

### OpeningHours

Converted to an OSM opening hours string. `closed` entries are dropped. `00:00 - 00:00` is treated as open all day; if
all seven days are open all day the result is `24/7`. Identical Monday–Friday times are summarized to a `Mo-Fr` entry,
otherwise each weekday is listed separately; Saturday and Sunday are always handled separately.

| Field        | Type                | Cardinality | Mapping       | Comment                                         |
|--------------|---------------------|-------------|---------------|-------------------------------------------------|
| Weekday      | [Weekday](#Weekday) | 1           | opening_hours |                                                 |
| OpeningTimes | string              | 1           | opening_hours | e.g. `08:00 - 20:00`, `closed`, `00:00 - 00:00` |

### IndicativeTariff

Only used to derive `has_fee`: if either `MinValue` or `MaxValue` is set, `has_fee` becomes `True`. All other fields are
validated but not mapped.

| Field        | Type    | Cardinality | Mapping | Comment                  |
|--------------|---------|-------------|---------|--------------------------|
| MinPrefix    | string  | ?           |         |                          |
| MinValue     | numeric | ?           | has_fee | sets `has_fee` to `True` |
| MinSuffix    | string  | ?           |         |                          |
| MaxPrefix    | string  | ?           |         |                          |
| MaxValue     | numeric | ?           | has_fee | sets `has_fee` to `True` |
| MaxSuffix    | string  | ?           |         |                          |
| Currency     | string  | ?           |         |                          |
| CurrencyCode | string  | ?           |         |                          |
| TaxRate      | numeric | ?           |         |                          |

## Enumerations

### CarparkType

Mapped from `CarparkType.Name` to `type`. Any other value falls back to `OTHER`.

| Key                    | Mapping                   |
|------------------------|---------------------------|
| MLCP                   | CAR_PARK                  |
| Off-street open        | OFF_STREET_PARKING_GROUND |
| Off-street underground | UNDERGROUND               |
| On-street              | ON_STREET                 |
| Open Surface           | OFF_STREET_PARKING_GROUND |

### SpaceType

The `Type` of each `Spaces` entry. `Total Spaces` becomes the `capacity`; the following types are mapped to a
`restriction` with the given `ParkingAudience`. `Urban Hubs reserved` and any unlisted type are ignored.

| Key                                             | Mapping (restriction type) |
|-------------------------------------------------|----------------------------|
| Total Spaces                                    | capacity                   |
| Disabled Spaces                                 | DISABLED                   |
| Women Spaces                                    | WOMEN                      |
| Electric Car Charging Spaces                    | CHARGING                   |
| Electric Car Fast Charging Spaces               | CHARGING                   |
| EV Charging                                     | CHARGING                   |
| EV Charging Bays                                | CHARGING                   |
| Car rental & sharing (weekdays from 8am to 8pm) | CARSHARING                 |
| PickUp&DropOff (weekdays from 8pm to 8am)       | CARSHARING                 |
| Carsharing Spaces                               | CARSHARING                 |
| Bus/Coaches Spaces                              | BUS                        |
| Family Spaces                                   | FAMILY                     |
| Urban Hubs reserved                             | ignored                    |

### Weekday

Used to build the OSM opening hours string.

| Key       | Mapping |
|-----------|---------|
| Monday    | Mo      |
| Tuesday   | Tu      |
| Wednesday | We      |
| Thursday  | Th      |
| Friday    | Fr      |
| Saturday  | Sa      |
| Sunday    | Su      |
