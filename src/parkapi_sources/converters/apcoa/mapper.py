"""
Copyright 2024 binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

from parkapi_sources.models import StaticParkingSiteInput
from parkapi_sources.models.enums import PurposeType

from .validators import (
    ApcoaNavigationLocationType,
    ApcoaParkingSiteInput,
    ApcoaParkingSpaceType,
)


class ApcoaMapper:
    @staticmethod
    def map_static_parking_site(
        apcoa_input: ApcoaParkingSiteInput,
    ) -> StaticParkingSiteInput:
        latitude, longitude = next(
            iter(
                (
                    navigation_locations_input.GeoCoordinates.Latitude,
                    navigation_locations_input.GeoCoordinates.Longitude,
                )
                for navigation_locations_input in apcoa_input.NavigationLocations
                if navigation_locations_input.LocationType == ApcoaNavigationLocationType.DEFAULT
            )
        )
        if apcoa_input.CarparkType is None:
            parking_site_type = None
        else:
            parking_site_type = apcoa_input.CarparkType.Name.to_parking_site_type_input()

        static_parking_site_input = StaticParkingSiteInput(
            uid=str(apcoa_input.CarParkId),
            name=apcoa_input.CarparkLongName if apcoa_input.CarparkLongName else apcoa_input.CarparkShortName,
            lat=latitude,
            lon=longitude,
            purpose=PurposeType.CAR,
            type=parking_site_type,
            has_realtime_data=False,  # TODO: change this as soon as Apcoa API offers realtime data
            public_url=apcoa_input.CarParkWebsiteURL,
            static_data_updated_at=apcoa_input.LastModifiedDateTime,
            # Because it was checked in validation, we can be sure that capacity will be set
            capacity=next(
                iter(item.Count for item in apcoa_input.Spaces if item.Type == ApcoaParkingSpaceType.TOTAL_SPACES),
            ),
        )

        if apcoa_input.Address.Street and apcoa_input.Address.Zip and apcoa_input.Address.City:
            static_parking_site_input.address = (
                f'{apcoa_input.Address.Street}, {apcoa_input.Address.Zip} {apcoa_input.Address.City}'
            )

        if apcoa_input.CarParkPhotoURLs:
            static_parking_site_input.photo_url = apcoa_input.CarParkPhotoURLs.CarparkPhotoURL1

        if apcoa_input.IndicativeTariff.MinValue or apcoa_input.IndicativeTariff.MaxValue:
            static_parking_site_input.has_fee = True

        static_parking_site_input.opening_hours = apcoa_input.get_osm_opening_hours()

        # Map all additional capacities
        for capacity_data in apcoa_input.Spaces:
            if capacity_data.Type == ApcoaParkingSpaceType.DISABLED_SPACES:
                static_parking_site_input.capacity_disabled = capacity_data.Count
            elif capacity_data.Type == ApcoaParkingSpaceType.WOMEN_SPACES:
                static_parking_site_input.capacity_woman = capacity_data.Count
            elif capacity_data.Type in [
                ApcoaParkingSpaceType.ELECTRIC_CAR_CHARGING_SPACES,
                ApcoaParkingSpaceType.ELECTRIC_CAR_FAST_CHARGING_SPACES,
                ApcoaParkingSpaceType.EV_CHARGING,
                ApcoaParkingSpaceType.EV_CHARGING_BAYS,
            ]:
                static_parking_site_input.capacity_charging = capacity_data.Count
            elif capacity_data.Type in [
                ApcoaParkingSpaceType.CAR_RENTAL_AND_SHARING,
                ApcoaParkingSpaceType.PICKUP_AND_DROPOFF,
                ApcoaParkingSpaceType.CARSHARING_SPACES,
            ]:
                static_parking_site_input.capacity_carsharing = capacity_data.Count
            elif capacity_data.Type == ApcoaParkingSpaceType.BUS_OR_COACHES_SPACES:
                static_parking_site_input.capacity_bus = capacity_data.Count
            elif capacity_data.Type == ApcoaParkingSpaceType.FAMILY_SPACES:
                static_parking_site_input.capacity_family = capacity_data.Count

        return static_parking_site_input
