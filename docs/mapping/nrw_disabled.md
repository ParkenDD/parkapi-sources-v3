# NRW.Mobidrom: Behindertenparkplätze NRW

NRW.Mobidrom publishes bundled static data of parking sites for people with disabilities in North Rhine-Westphalia
(currently Bielefeld, Dortmund and Köln) via the
[Mobilithek](https://mobilithek.info/offers/1029367261516726272). The data offer declares DATEX II 2.3 as XML, so the
converter uses the generic class `UrbanParkingSiteMixin`. There is no realtime data, so just the static subscription
`PARK_API_MOBILITHEK_NRW_DISABLED_STATIC_SUBSCRIPTION_ID` is required.

**Broken:** the data is not valid DATEX II, as it does not match its declared data model: the publication is JSON in
the structure of a DATEX II v3 `ParkingPublicationLight` instead of DATEX II 2.3 XML. The static import fails with a
single error, as the publication cannot be parsed as XML, and no parking site is imported. The following table
describes the delivered data, which is not mapped.

Static values:

* `has_realtime_data` is always `false`

## Static data

The JSON object has a `modelBaseVersion` of `3` and a `parkingPublicationLight` with `publicationTime` and a list of
`parkingSite`.

| Field                                                | Type    | Cardinality | Mapping | Comment                                                                |
|------------------------------------------------------|---------|-------------|---------|------------------------------------------------------------------------|
| id                                                   | string  | 1           |         | e.g. `parking-disabled-koeln-385`                                      |
| type                                                 | enum    | 1           |         | always `other`                                                         |
| name                                                 | string  | ?           |         | mostly the address, missing at the Dortmund parking sites              |
| description                                          | string  | 1           |         | mostly `Behindertenparkplätze`, at Dortmund e.g. `öffentlich`          |
| numberOfSpaces                                       | integer | ?           |         | mostly `1` or `2`, missing at the Dortmund parking sites               |
| zoneDescription                                      | string  | ?           |         | just at the Dortmund parking sites                                     |
| openingTimesDescription                              | string  | ?           |         |                                                                        |
| locationAndDimension.locationDescriptor              | string  | 1           |         | address with city                                                      |
| locationAndDimension.specificAccessInformation       | string  | *           |         | e.g. `Parkplatz`                                                       |
| locationAndDimension.roadName                        | string  | ?           |         |                                                                        |
| locationAndDimension.roadNumber                      | string  | ?           |         |                                                                        |
| locationAndDimension.coordinatesForDisplay.latitude  | numeric | 1           |         |                                                                        |
| locationAndDimension.coordinatesForDisplay.longitude | numeric | 1           |         |                                                                        |
