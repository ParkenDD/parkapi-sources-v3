# Bundesautobahn rest areas

The Bundesministerium für Verkehr provides a large Datex II publication for managed and unmanaged truck and car parking spaces at motorways.
A parking space is represented by a `parkingRecord`. For each `parkingRecord` a `ParkingSite` is generated:

* `purpose` is set to `CAR`
* `type` is set to `OFF_STREET_PARKING_GROUND`
* `opening_hours` is set to `24/7`
* `has_realtime_data` is set to `false`

| Field                         | Type                                         | Cardinality | Mapping                                   | Comment                                                    |
|-------------------------------|----------------------------------------------|-------------|-------------------------------------------|------------------------------------------------------------|
| type                          | enum                                         | 1           |                                           | always `InterUrbanParkingSite`
| id                            | string                                       | 1           | uid                                       |
| version                       | integer                                      | 1
| parkingName.value[de]         | string                                       | 1           | name
| parkingAlias.value[de]        | string                                       | ?
| parkingDescription.value[de]  | string                                       | 1           |                                           | mostly administrative information
| parkingRecordVersionTime      | datetime                                     | 1           | static_data_updated_at
| parkingNumberOfSpaces         | integer                                      | 1           | capacity                                  | if ==0 set to 1
| parkingOccupanyDetectionType  | enum                                         | 1           |                                           | always `unknown`
| operator.contactOrganisationName.value[de] | string                          | ?           | operator_name                             | map `&amp;` to `&`
| operator.contactDetailsTelephoneNumber     | string                          | ?
| operator.contactDetailsFax                 | string                          | ?
| operator.urlLinkAddress                    | string                          | ?
| operator.publishingAgreement               | boolean                         | ?
| operator.contactUnknown                    | boolean                         | ?
| parkingLocation.pointCoordinates.latitude  | numeric                         | 1           | lat
| parkingLocation.pointCoordinates.longitude | numeric                         | 1           | lon
| tariffsAndPayment.freeOfCharge             | boolean                         | 1           | has_fee                                   | always true, has_fee=not(freeOfCharge)
| parkingEquipmentOrServiceFacility[type].availability | boolean               | ?           |                                           | type == refuseBin / toilet / shower / tollTerminal / motorwayRestaurant / picnicFacilities / ...
| groupOfParkingSpaces.vehicleCharacteristics[lorry]               | integer   | 1           | restriction[TRUCK].capacity               | set only if != 0
| groupOfParkingSpaces.vehicleCharacteristics[car]                 | integer   | 1
| groupOfParkingSpaces.vehicleCharacteristics[refrigeratedGoods]   | integer   | 1
| groupOfParkingSpaces.vehicleCharacteristics[bus]                 | integer   | 1           | restriction[BUS].capacity                 | set only if != 0
| groupOfParkingSpaces.vehicleCharacteristics[carWithTrailer]      | integer   | 1
| groupOfParkingSpaces.vehicleCharacteristics[heavyHaulageVehicle] | integer   | 1
| parkingReservation                                               | enum      | 1           |                                           | always `unknown`
| parkingSiteAddress.contactDetailsStreet                          | string    | ?           | address                                   | set only if not contains "n/a"
| parkingSiteAddress.contactDetailsHouseNumber                     | string    | ?           | address                                   | set only if not contains "n/a"
| parkingSiteAddress.contactDetailsPostcode                        | string    | ?           | address                                   | set only if not contains "n/a"
| parkingSiteAddress.contactDetailsCity.value[de]                  | string    | ?           | address                                   | set only if not contains "n/a"
| parkingSiteAddress.contactDetailsStreet.country                  | string    | ?           |                                           | always "de"
| parkingSiteAddress.contactUnknown                                | boolean   | ?
| parkingUsageScenario[truckParking].truckParkingDynamicManagement | enum      | 1           |                                           | always `noDynamicParkingManagement`
| parkingUsageScenario[restArea]                                   | null      | 1
| parkingAccess                                                    |           | *
| parkingStandardsAndSecurity                                      |           | 1
| interUrbanParkingSiteLocation                                    | enum      | 1           |                                           | always `motorway`
| interUrbanParkingSiteExtension                                   | null      | 1
