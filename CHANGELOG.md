# Changelog

## 0.30.1

Released 2025-11-12

### Features

* [bfrk: add missing base class](https://github.com/ParkenDD/parkapi-sources-v3/pull/302)


## 0.30.0

Released 2025-11-10

### Features

* [bfrk disabled spots](https://github.com/ParkenDD/parkapi-sources-v3/pull/300)


## 0.29.0

Released 2025-11-03

### Features

* [Add Freiburg VAG bike boxes](https://github.com/ParkenDD/parkapi-sources-v3/pull/296)


## 0.28.0

Released 2025-10-20

This release is breaking by normalizing `restrictions` and therefore removing `capacity_{audience}` from
`StaticParkingSiteInput` and `RealtimeParkingSiteInput`.

### Features

* [restrictions system](https://github.com/ParkenDD/parkapi-sources-v3/pull/295)


## 0.27.1

Released 2025-10-14

### Fixes

* [Change Enum ParkingSiteType to ParkingSpotType at Sensade](https://github.com/ParkenDD/parkapi-sources-v3/pull/293)


## 0.27.0

Released 2025-10-13

### Features

* [Integrate P+M or carpooling from Sensade API](https://github.com/ParkenDD/parkapi-sources-v3/pull/288)


### Fixes

* [kienzler: change public_url to use direct_link value](https://github.com/ParkenDD/parkapi-sources-v3/pull/290)
* [ensure valid osm opening times](https://github.com/ParkenDD/parkapi-sources-v3/pull/289)


## 0.26.2

Released 2025-09-15

### Fixes

* [allow linestrings at radolfzell](https://github.com/ParkenDD/parkapi-sources-v3/pull/285)


## 0.26.1

Released 2025-09-08

### Fixes

* [update spatial.vrn.de link](https://github.com/ParkenDD/parkapi-sources-v3/pull/280)
* Better emptystring handling in `heidelberg_disabled`


### Maintenance

* Dependency updates


## 0.26.0

Released 2025-08-31

### Features

* [Kienzler: Ulm Converter](https://github.com/ParkenDD/parkapi-sources-v3/pull/277)
* [Radolfzell Converter](https://github.com/ParkenDD/parkapi-sources-v3/pull/276)
* [Ladenburg Parkraumcheck Converter](https://github.com/ParkenDD/parkapi-sources-v3/pull/275)
* [Karlsruhe Disabled Converter](https://github.com/ParkenDD/parkapi-sources-v3/pull/274)
* [Heidelberg Disabled Converter](https://github.com/ParkenDD/parkapi-sources-v3/pull/273)


### Fixes

* [bfrk validation errors for osmlinks](https://github.com/ParkenDD/parkapi-sources-v3/pull/272)
* [Fix missing konstanz data: made realtime data optional](https://github.com/ParkenDD/parkapi-sources-v3/pull/271)


## 0.25.0

Released 2025-08-15

This is a maintenance release with major dependency updates and a minimal python version bump to python 3.12.

### Fixes

* [fix patching system subobjects](https://github.com/ParkenDD/parkapi-sources-v3/pull/268)
* [Heidelberg: Fix uid mismatch and missing realtime data](https://github.com/ParkenDD/parkapi-sources-v3/pull/267)
* [freiburg scanner address](https://github.com/ParkenDD/parkapi-sources-v3/pull/266)
* [better pbw realtime data field](https://github.com/ParkenDD/parkapi-sources-v3/pull/265)


### Maintenance

* Several dependency updates, most notably `lxml` 5.x -> 6.x.
* Change the minimal python version to 3.12 due `pyproj` 3.7.2


## 0.24.0

Released 2025-08-11

### Features

* [Aalen converter](https://github.com/ParkenDD/parkapi-sources-v3/pull/258)
* [Unify Patching to support ParkingSpot patches](https://github.com/ParkenDD/parkapi-sources-v3/pull/260)
* [Konstanz Disabled converter](https://github.com/ParkenDD/parkapi-sources-v3/pull/257)


### Fixes

* [Bahn_v2: Add park_and_ride_type=TRAIN](https://github.com/ParkenDD/parkapi-sources-v3/pull/259)


## 0.23.0

Released 2025-07-28

### Maintenance

* [remove kienzler geojson](https://github.com/ParkenDD/parkapi-sources-v3/pull/255)

This release actually removes a feature, the Kienzler-specific GeoJSON patch mechanism, as there is now a
[generic patch mechanism](https://github.com/ParkenDD/parkapi-sources-v3/blob/01df26ed963a424d9b1165b1b4e8cd5e9ed83b20/README.md#patch-data-with-local-files).


## 0.22.0

### Features

* [Synchronize and extend data model](https://github.com/ParkenDD/parkapi-sources-v3/pull/249)
* [Esslingen Converter](https://github.com/ParkenDD/parkapi-sources-v3/pull/250)
* [Freiburg Scanner Converter](https://github.com/ParkenDD/parkapi-sources-v3/pull/251)
* [Heidelberg EasyPark Converter](https://github.com/ParkenDD/parkapi-sources-v3/pull/252)
* [Keltern Converter](https://github.com/ParkenDD/parkapi-sources-v3/pull/253)
* [Reutlingen Disabled Converter](https://github.com/ParkenDD/parkapi-sources-v3/pull/254)


## 0.21.1

Released 2025-07-21

### Fixes

* [Extend Friedrichshafen](https://github.com/ParkenDD/parkapi-sources-v3/pull/244)


### Maintenance

* Dependency Updates


## 0.21.0

Released 2025-07-14

### Features

* [Integrate B+B Parkhaus Push Converter](https://github.com/ParkenDD/parkapi-sources-v3/pull/237)


### Fixes

* [Freiburg: fixed closed status](https://github.com/ParkenDD/parkapi-sources-v3/pull/242)
* [recreate Makefile](https://github.com/ParkenDD/parkapi-sources-v3/pull/241)


## 0.20.1

Released 2025-07-07

### Fixes

* [Freiburg P+R Attribute](https://github.com/ParkenDD/parkapi-sources-v3/pull/235)
* [Freiburg OpeningTime logic](https://github.com/ParkenDD/parkapi-sources-v3/pull/234)


## 0.20.0

Released 2025-06-23

### Features

* [Freiburg P+R Converters](https://github.com/ParkenDD/parkapi-sources-v3/pull/230)


## 0.19.4

Released 2025-06-02

### Fixes

* [Extend static data to Freiburg](https://github.com/ParkenDD/parkapi-sources-v3/pull/226)


## 0.19.3

Released 2025-05-18

### Fixes

* [ensures correct typing in child objects](https://github.com/ParkenDD/parkapi-sources-v3/pull/217)
* [register Freiburg converters properly](https://github.com/ParkenDD/parkapi-sources-v3/pull/217)


### Maintenance

* [Add project URLs ty PyPI](https://github.com/ParkenDD/parkapi-sources-v3/pull/217)


## 0.19.2

Released 2025-05-18

### Fixes

* Fix typo in description property


## 0.19.1

Released 2025-05-18

### Fixes

* Add missing dependencies to pyproject.toml


## 0.19.0

Released: 2025-05-18

### Features

* [ParkingSite patch system](https://github.com/ParkenDD/parkapi-sources-v3/pull/208)
* [Freiburg ParkingSpots](https://github.com/ParkenDD/parkapi-sources-v3/pull/214)
* [Ulm Sensors ParkingSites and ParkingSpots](https://github.com/ParkenDD/parkapi-sources-v3/pull/203)
* [ParkingSpot type support for Friedrichshafen Sensors](https://github.com/ParkenDD/parkapi-sources-v3/pull/213)


### Maintenance

* [Dependency updates](https://github.com/ParkenDD/parkapi-sources-v3/pull/216)


## 0.18.2

Released 2025-05-10

### Fixes

* [better datex2 handling and testing](https://github.com/ParkenDD/parkapi-sources-v3/pull/212)


## 0.18.1

Released 2025-05-08

### Fixes

* [better handling of mobilithek pull mechanisms](https://github.com/ParkenDD/parkapi-sources-v3/pull/211)


## 0.18.0

Released 2025-04-02

This release is a major change, as it introduces parking spots. If you used internal objects, this update might be
breaking for you. Existing converters will work exactly the same and have the same interface, so for most users,
updating will be fine.

### Features

* [ParkingSpot support](https://github.com/ParkenDD/parkapi-sources-v3/pull/198)
* [Friedrichshafen parking spot sensor data](https://github.com/ParkenDD/parkapi-sources-v3/pull/198)


## 0.17.4

Released 2025-04-01

### Fixes

* [Update pum_bw mapping and data](https://github.com/ParkenDD/parkapi-sources-v3/pull/197)
* [Changed source_url for herrenberg_bike](https://github.com/ParkenDD/parkapi-sources-v3/pull/194)


## 0.17.3

Released 2025-03-07

### Fixes

* [Fix and reduce validation errors in converters](https://github.com/ParkenDD/parkapi-sources-v3/pull/191)


## 0.17.2

Released 2025-02-22

### Fixes

* [introduce request helper](https://github.com/ParkenDD/parkapi-sources-v3/pull/190)


## 0.17.1

Released 2025-02-19

### Fixes

* [Fix bahn converter by creating session for client cert requests](https://github.com/ParkenDD/parkapi-sources-v3/pull/189)


## 0.17.0

Released 2025-02-19

## Features

* [Add Aachen](https://github.com/ParkenDD/parkapi-sources-v3/pull/186)
* [Debug Mode for dumping full communication per source](https://github.com/ParkenDD/parkapi-sources-v3/pull/187)


## Maintenance

* [Datex2 Refactoring for good parent classes for any Datex2 source](https://github.com/ParkenDD/parkapi-sources-v3/pull/186)


## 0.16.1

Released 2025-02-01

### Fixes

* [Add required attributes at several converters](https://github.com/ParkenDD/parkapi-sources-v3/pull/183)


### Maintenance

* Dependency updates


## 0.16.0

Released 2025-01-21

### Features

* [Add VRN Park and Ride Realtime Converter](https://github.com/ParkenDD/parkapi-sources-v3/pull/180)
* [Add bahnv2 bike parking locked and open](https://github.com/ParkenDD/parkapi-sources-v3/pull/172)

### Fixes

* [opendata_swiss: change to new source_url](https://github.com/ParkenDD/parkapi-sources-v3/pull/179)


## 0.15.1

Released 2024-11-27

### Fixes

* [GeoJSON Approach cleanup](https://github.com/ParkenDD/parkapi-sources-v3/pull/173)
* [Fix DateTime Format at Karlsruhe](https://github.com/ParkenDD/parkapi-sources-v3/pull/173)
* [Fix optional attributes at Kienzler](https://github.com/ParkenDD/parkapi-sources-v3/pull/173)
* Code cleanup


## 0.15.0

Released 2024-11-25

## Features

* [New Source: Velobrix](https://github.com/ParkenDD/parkapi-sources-v3/pull/165)
* [Kienzler: use static data as additional data input](https://github.com/ParkenDD/parkapi-sources-v3/pull/168)


## 0.14.2

Released 2024-11-12

### Fixes

* [APCOA: Remove park control objects and added production endpoint](https://github.com/ParkenDD/parkapi-sources-v3/pull/162)
* [radvis_bw: filter unprintable characters](https://github.com/ParkenDD/parkapi-sources-v3/pull/167)
* [multiple converters: set opening status to none if unset](https://github.com/ParkenDD/parkapi-sources-v3/pull/160)


## 0.14.1

Released 2024-10-29

### Fixes

* [Fixed Karlsruhe format for stand_stammdaten ](https://github.com/ParkenDD/parkapi-sources-v3/pull/152)
* [ruff modernization](https://github.com/ParkenDD/parkapi-sources-v3/pull/155)


## 0.14.0

Released 2024-10-17

### Features

* [Add Kienzler VVS Converter](https://github.com/ParkenDD/parkapi-sources-v3/pull/147)


### Fixes

* [Update pbw data for static parking sites](https://github.com/ParkenDD/parkapi-sources-v3/pull/144)
* [Update kienzler data for static parking sites](https://github.com/ParkenDD/parkapi-sources-v3/pull/145)
* [Fix bfrk_bw_car attribute after source change](https://github.com/ParkenDD/parkapi-sources-v3/pull/149)


## 0.13.3

Released 2024-10-07

### Fixes

* [Fix BFRK infraid](https://github.com/ParkenDD/parkapi-sources-v3/pull/140)


## 0.13.2

Released 2024-09-24

### Fixes

* [enforce capacity](https://github.com/ParkenDD/parkapi-sources-v3/pull/133)
* [remove confusing herrenberg field](https://github.com/ParkenDD/parkapi-sources-v3/pull/134)
* [set kienzler public url](https://github.com/ParkenDD/parkapi-sources-v3/pull/135)
* [fix Herrenberg parking type mapping](https://github.com/ParkenDD/parkapi-sources-v3/pull/136)


## 0.13.1

Release 2024-09-22

### Fixes

* [Add VRS data](https://github.com/ParkenDD/parkapi-sources-v3/pull/123)
* [Fix bahn mapping](https://github.com/ParkenDD/parkapi-sources-v3/pull/124)
* [Fix PBW Mapping](https://github.com/ParkenDD/parkapi-sources-v3/pull/125)
* [Fix Heidelberg fee](https://github.com/ParkenDD/parkapi-sources-v3/pull/126)
* [Split up kienzler requests](https://github.com/ParkenDD/parkapi-sources-v3/pull/128)
* [Fix bfrk mapping](https://github.com/ParkenDD/parkapi-sources-v3/pull/129)


## 0.13.0

Released 2024-09-16

### Features

* [Herrenberg static bike pull converter](https://github.com/ParkenDD/parkapi-sources-v3/pull/110)


### Fixes

* [Park and Ride at BFRK](https://github.com/ParkenDD/parkapi-sources-v3/pull/121)


## 0.12.1

Released 2024-09-09

### Fixes

* [has_fee True at all Heidelberg parking sites](https://github.com/ParkenDD/parkapi-sources-v3/pull/117)


## 0.12.0

Released 2024-09-03

### Features

* [Hüfner Push Converter](https://github.com/ParkenDD/parkapi-sources-v3/pull/106)


### Fixes

* [BFRK: Make URL configurable](https://github.com/ParkenDD/parkapi-sources-v3/pull/114)
* [Karlsruhe Bike: Ignore missing capacities](https://github.com/ParkenDD/parkapi-sources-v3/pull/113)
* [APCOA: Ignore missing coordinates](https://github.com/ParkenDD/parkapi-sources-v3/pull/112)
* [APCOA: Fix OSM Opening Times](https://github.com/ParkenDD/parkapi-sources-v3/pull/107)


## 0.11.0

Release 2024-08-24

### Features

* [BFRK: Use API](https://github.com/ParkenDD/parkapi-sources-v3/pull/109)


## 0.10.1

Release 2024-08-24

### Fixes

* [Dynamic Realtime Setting at Karlsruhe](https://github.com/ParkenDD/parkapi-sources-v3/pull/105)
* [Fixes VRS UID mapping](https://github.com/ParkenDD/parkapi-sources-v3/pull/108)


## 0.10.0

Released 2024-08-20

### Features

* [Converters for Bondorf, Kirchheim, Neustadt and Vaihingen](https://github.com/ParkenDD/parkapi-sources-v3/pull/98)
* [Converter for Konstanz](https://github.com/ParkenDD/parkapi-sources-v3/pull/102)


### Fixes

* [fixes env vars at Kienzler split-up](https://github.com/ParkenDD/parkapi-sources-v3/pull/101)


## 0.9.0

Released 2024-08-15

### Features

* [parking site groups](https://github.com/ParkenDD/parkapi-sources-v3/pull/95)
* [split up kienzler](https://github.com/ParkenDD/parkapi-sources-v3/pull/96)


### Fixes

* [Karlsruhe converter: Updated parking place name and opening_status attributes](https://github.com/ParkenDD/parkapi-sources-v3/pull/94)


## 0.8.0

Released 2024-08-08

### Features

* [Opendata Swiss pull converter](https://github.com/ParkenDD/parkapi-sources-v3/pull/70)

### Fixes

* [Ellwangen converter: Added OSM opening_hours](https://github.com/ParkenDD/parkapi-sources-v3/pull/90)
* [Updated the source_url Karlsruhe converter](https://github.com/ParkenDD/parkapi-sources-v3/pull/88)
* [Goldbeck converter: Added OSM opening_hours](https://github.com/ParkenDD/parkapi-sources-v3/pull/89)


## 0.7.1

Released 2024-07-25

### Fixes

* [Fix Ulm scraper](https://github.com/ParkenDD/parkapi-sources-v3/pull/82)
* [Fix Herrenberg address](https://github.com/ParkenDD/parkapi-sources-v3/pull/83)
* [Fix Herrenberg state mapping](https://github.com/ParkenDD/parkapi-sources-v3/pull/84)
* [Fix BFRK is_covered naming](https://github.com/ParkenDD/parkapi-sources-v3/pull/85)


## 0.7.0

Released 2024-07-23

### Features

* [Goldbeck support](https://github.com/ParkenDD/parkapi-sources-v3/pull/68)


## 0.6.2

Released 2024-07-23

### Fixes

* [Fix Karlsruhe converter after Karlsruhe made changes](https://github.com/ParkenDD/parkapi-sources-v3/pull/74)


## 0.6.1

Released 2024-07-13

### Fixes

* [Fix Herrenberg base class](https://github.com/ParkenDD/parkapi-sources-v3/pull/73)


## 0.6.0

Released 2024-07-13

### Features

* [Add Herrenberg converter](https://github.com/ParkenDD/parkapi-sources-v3/pull/71)
* [Add APCOA converter](https://github.com/ParkenDD/parkapi-sources-v3/pull/72)


## 0.5.3

Released 2024-06-19

### Fixes

* [set karlsruhe to realtime](https://github.com/ParkenDD/parkapi-sources-v3/pull/65)


## 0.5.2

Released 2024-06-18

### Fixes

* [Add ACTIVE status to P+M BW Converter](https://github.com/ParkenDD/parkapi-sources-v3/pull/64)


## 0.5.1

Released 2024-06-18

### Fixes

* [Renames and extends P+M BW Converter with static data](https://github.com/ParkenDD/parkapi-sources-v3/pull/63)


## 0.5.0

Release 2024-06-14

### Features

* [Own repository for static data](https://github.com/ParkenDD/parkapi-sources-v3/pull/53)
* [A81 P&M Converter](https://github.com/ParkenDD/parkapi-sources-v3/pull/55)
* [Bietigheim-Bissingen Converter](https://github.com/ParkenDD/parkapi-sources-v3/pull/57)
* [Heidelberg Converter](https://github.com/ParkenDD/parkapi-sources-v3/pull/58)


### Fixes

* [Fix Freiburg timezone](https://github.com/ParkenDD/parkapi-sources-v3/pull/54)
* [https://github.com/ParkenDD/parkapi-sources-v3/pull/56](https://github.com/ParkenDD/parkapi-sources-v3/pull/56)
* [Better Freiburg Converter](https://github.com/ParkenDD/parkapi-sources-v3/pull/59)


### Maintenance

* Replace black by ruff formatter
* Dependency updates


## 0.4.4

Released 2024-06-04

### Fixes:

* [Fixes an issue with wrong koordinates at Karlsruhe](https://github.com/ParkenDD/parkapi-sources-v3/pull/48)
* [Fixes an issue with Bahn data without capacity](https://github.com/ParkenDD/parkapi-sources-v3/pull/49)


## 0.4.3

Released 2024-05-29

### Fixes:

* [Fixes an issue with coordinates at XLSX base converter](https://github.com/ParkenDD/parkapi-sources-v3/pull/45)


## 0.4.2

Released 2024-05-16

### Fixes:

* Fixes purpose to BIKE at RadVIS bike converter


## 0.4.1

Released 2024-05-16

### Fixes:

* Fixes purpose to BIKE at Konstanz, Karlsruhe and RadVIS bike converters
* Fixes Karlsruhe bike converter uid
* Fixes Karlsruhe converter because data source changed date format


## 0.4.0

Released 2024-05-16

### Features

* Converter: [Konstanz Bike](https://github.com/ParkenDD/parkapi-sources-v3/pull/36), including some enumeration enhancements
* Converter: [Ellwangen](https://github.com/ParkenDD/parkapi-sources-v3/pull/26)
* Converter: [Karlsruhe Bike](https://github.com/ParkenDD/parkapi-sources-v3/pull/29)
* Experimental Converter: [RadVIS](https://github.com/ParkenDD/parkapi-sources-v3/pull/33), including some smaller model enhancements


### Fixes:

* Add static attributes [at `pub_bw` Converter](https://github.com/ParkenDD/parkapi-sources-v3/pull/32)
* Mannheim and Buchen [updated their data format to ParkAPI](https://github.com/ParkenDD/parkapi-sources-v3/pull/37)


## 0.3.1

Released 2024-05-03

### Fixes:

* Register neckarsulm_bike and reutlingen_bike properly


## 0.3.0

Released 2024-05-02

### Features:

* Automated tests via CI pipeline
* Converter: [Neckarsulm bike](https://github.com/ParkenDD/parkapi-sources-v3/pull/27)
* Converter: [Kienzler](https://github.com/ParkenDD/parkapi-sources-v3/pull/22)
* Converter: [Mannheim and Buchen](https://github.com/ParkenDD/parkapi-sources-v3/pull/21)
* Converter: [Reutlingen bike](https://github.com/ParkenDD/parkapi-sources-v3/pull/28)
* Converter: [Baden-Württemberg: Park und Mitfahren](https://github.com/ParkenDD/parkapi-sources-v3/pull/18)

### Fixes:

* [Fix required key at Heidelberg converter](https://github.com/ParkenDD/parkapi-sources-v3/pull/20)


## 0.2.0

Released 2024-04-18

First release including [public PyPI package](https://pypi.org/project/parkapi-sources/).
