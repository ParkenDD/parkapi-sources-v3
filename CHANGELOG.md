# Changelog


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
