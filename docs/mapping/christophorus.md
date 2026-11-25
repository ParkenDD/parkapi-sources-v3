# Florence Knuellwald: Lkw-Parkplatz Christophorus

The Florence Knuellwald GmbH publishes its truck parking site Christophorus near Kassel as Datex II v3 via the
[Mobilithek](https://mobilithek.info/offers/872174540205998080). The data offers declare the profiles
`Parkraummanagement_DATEX_II_v3_Grunddaten` (static data) and `Parkraummanagement_DATEX_II_v3_Belegungsdaten`
(realtime data). Therefore the converter uses the generic classes `UrbanParkingSiteV3Mixin` and
`ParkingRecordStatusV3Mixin`, which handle these profiles.

**Broken:** the data is not valid DATEX II, as it does not validate against its declared profiles:

* the `payload` is wrapped in a `messageContainer`, so the root element is `messageContainer` instead of `payload`
* the static data describes the parking site as `hierarchyElementGeneral` of type `ParkingArea` with elements of the
  `facilities` namespace instead of a `parkingRecord`, and lacks the required `headerInformation`
* the realtime data uses `parkingStatusInformation` instead of `parkingRecordStatus`

Because of the root element, both imports fail with a single error and no parking site is imported. The following
tables describe the delivered data, which is not mapped.

## Static data

`ParkingTablePublication` with one `parkingTable`, containing one `hierarchyElementGeneral`.

| Datex II field                            | Type     | Cardinality | Mapping | Comment                                |
|-------------------------------------------|----------|-------------|---------|----------------------------------------|
| @type                                     | enum     | 1           |         | `xsi:type`, always `ParkingArea`       |
| @id                                       | string   | 1           |         | always `christophorus-parking`         |
| fac:name.values.value                     | string   | 1           |         | `Christophorus Parking`                |
| fac:lastUpdated                           | datetime | 1           |         |                                        |
| fac:description.values.value              | string   | 1           |         |                                        |
| fac:informationWebsite.urlLinkAddress     | string   | 1           |         | `https://www.christophorus-parking.de` |
| fac:operatingHours                        | object   | 1           |         | `xsi:type`, always `OpenAllHours`      |
| loc:location.pointByCoordinates.gml:Point | string   | 1           |         | `gml:pos` with latitude and longitude  |
| prk:totalCapacity                         | integer  | 1           |         | `68`                                   |
| fac:applicableForVehicles.vehicleType     | enum     | 1           |         | always `lorry`                         |
| fac:services.facilityObject.type          | enum     | *           |         | e.g. `toilet`, `shower`                |

The publication contains a `fac:rateTable` next to the `parkingTable` with a rate of 2.50 EUR per hour.

## Realtime data

`ParkingStatusPublication` with one `parkingStatusInformation`.

| Datex II field                   | Type     | Cardinality | Mapping | Comment                                         |
|----------------------------------|----------|-------------|---------|-------------------------------------------------|
| fac:reference.@id                | string   | 1           |         | references the static `hierarchyElementGeneral` |
| fac:lastUpdated                  | datetime | 1           |         |                                                 |
| occupancy.numberOfVacantSpaces   | integer  | 1           |         |                                                 |
| occupancy.numberOfOccupiedSpaces | integer  | 1           |         |                                                 |
| occupancy.occupancy              | integer  | 1           |         | occupancy in percent                            |
