"""
Copyright 2024 binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

from datetime import datetime, timezone

from parkapi_sources.models import StaticParkingSiteInput

from .validators import ApcoaParkingSiteInput, ApcoaParkingSpaceType, NavigationLocationType, OpeningHoursWeekdays


class ApcoaMapper:
    @staticmethod
    def map_static_parking_site(apcoa_input: ApcoaParkingSiteInput) -> StaticParkingSiteInput:
        static_parking_site_input = StaticParkingSiteInput(
            uid=str(apcoa_input.id.CarParkId),
            name=apcoa_input.name.CarparkLongName if apcoa_input.name.CarparkLongName else apcoa_input.name.CarparkShortName,
            lat=next(
                iter(
                    location_type_input.Geocoordinates.Latitude
                    for location_type_input in apcoa_input.address.NavigationLocations
                    if location_type_input.LocationType == NavigationLocationType.DEFAULT
                )
            ),
            lon=next(
                iter(
                    location_type_input.Geocoordinates.Longitude
                    for location_type_input in apcoa_input.address.NavigationLocations
                    if location_type_input.LocationType == NavigationLocationType.DEFAULT
                )
            ),
            purpose=apcoa_input.purpose.CAR,
            address=f'{apcoa_input.address.Street}, {apcoa_input.address.Zip} {apcoa_input.address.City}',
            type=apcoa_input.type.CarparkType.Name.to_parking_site_type_input(),
            has_realtime_data=False,  # TODO: change this as soon as Apcoa API offers realtime data
            static_data_updated_at=datetime.now(tz=timezone.utc),
            public_url=apcoa_input.url,
        )
        num_of_weekdays = len(
            [
                opening_hours_input.Weekday
                for opening_hours_input in apcoa_input.opening_hours.OpeningHours
                if opening_hours_input.Weekday in OpeningHoursWeekdays.Weekdays
                and opening_hours_input.OpeningTimes == OpeningHoursWeekdays.OpeningTime
            ]
        )
        if num_of_weekdays == 7:
            static_parking_site_input.opening_hours = '24/7'

        for capacity_data in apcoa_input.capacity.Spaces:
            # Because it was checked in validation, we can be sure that capacity will be set
            if capacity_data.Type == ApcoaParkingSpaceType.TOTAL_SPACES:
                static_parking_site_input.capacity = int(round(capacity_data.Count))
            elif capacity_data.Type == ApcoaParkingSpaceType.DISABLED_SPACES:
                static_parking_site_input.capacity_disabled = int(round(capacity_data.Count))
            elif capacity_data.Type == ApcoaParkingSpaceType.WOMEN_SPACES:
                static_parking_site_input.capacity_woman = int(round(capacity_data.Count))
            elif capacity_data.Type == ApcoaParkingSpaceType.ELECTRIC_CAR_CHARGING_SPACES:
                static_parking_site_input.capacity_charging = int(round(capacity_data.Count))
            elif capacity_data.Type == ApcoaParkingSpaceType.ELECTRIC_CAR_FAST_CHARGING_SPACES:
                static_parking_site_input.capacity_charging = int(round(capacity_data.Count))
            elif capacity_data.Type == ApcoaParkingSpaceType.EV_CHARGING:
                static_parking_site_input.capacity_charging = int(round(capacity_data.Count))
            elif capacity_data.Type == ApcoaParkingSpaceType.EV_CHARGING_BAYS:
                static_parking_site_input.capacity_charging = int(round(capacity_data.Count))
            elif capacity_data.Type == ApcoaParkingSpaceType.CARSHARING_SPACES:
                static_parking_site_input.capacity_carsharing = int(round(capacity_data.Count))
            elif capacity_data.Type == ApcoaParkingSpaceType.CAR_RENTAL_AND_SHARING:
                static_parking_site_input.capacity_carsharing = int(round(capacity_data.Count))
            elif capacity_data.Type == ApcoaParkingSpaceType.PICKUP_AND_DROPOFF:
                static_parking_site_input.capacity_carsharing = int(round(capacity_data.Count))
            elif capacity_data.Type == ApcoaParkingSpaceType.BUS_OR_COACHES_SPACES:
                static_parking_site_input.capacity_bus = int(round(capacity_data.Count))
            elif capacity_data.Type == ApcoaParkingSpaceType.FAMILY_SPACES:
                static_parking_site_input.capacity_family = int(round(capacity_data.Count))

        return static_parking_site_input
