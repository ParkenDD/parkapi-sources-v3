"""
Copyright 2024 binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

from collections import defaultdict
from datetime import datetime, timezone

from parkapi_sources.models import StaticParkingSiteInput
from parkapi_sources.models.enums import PurposeType

from .validators import (
    ApcoaNavigationLocationType,
    ApcoaOpeningHoursTime,
    ApcoaOpeningHoursWeekdays,
    ApcoaParkingSiteInput,
    ApcoaParkingSpaceType,
)


class ApcoaMapper:
    @staticmethod
    def map_static_parking_site(apcoa_input: ApcoaParkingSiteInput) -> StaticParkingSiteInput:
        latitude, longitude = next(
            iter(
                (navigation_locations_input.GeoCoordinates.Latitude, navigation_locations_input.GeoCoordinates.Longitude)
                if navigation_locations_input.LocationType == ApcoaNavigationLocationType.DEFAULT
                else (None, None)
            )
            for navigation_locations_input in apcoa_input.NavigationLocations
        )

        static_parking_site_input = StaticParkingSiteInput(
            uid=str(apcoa_input.CarParkId),
            name=apcoa_input.CarparkLongName if apcoa_input.CarparkLongName else apcoa_input.CarparkShortName,
            lat=latitude,
            lon=longitude,
            purpose=PurposeType.CAR,
            type=apcoa_input.CarparkType.Name.to_parking_site_type_input(),
            has_realtime_data=False,  # TODO: change this as soon as Apcoa API offers realtime data
            public_url=apcoa_input.CarParkWebsiteURL,
            photo_url=apcoa_input.CarParkPhotoURLs.CarparkPhotoURL1,
            static_data_updated_at=apcoa_input.LastModifiedDateTime if apcoa_input.LastModifiedDateTime else datetime.now(tz=timezone.utc),
        )

        if apcoa_input.Address.Street and apcoa_input.Address.Zip and apcoa_input.Address.City:
            static_parking_site_input.address = f'{apcoa_input.Address.Street}, {apcoa_input.Address.Zip} {apcoa_input.Address.City}'

        apcoa_weekdays = [
            ApcoaOpeningHoursWeekdays.MONDAY,
            ApcoaOpeningHoursWeekdays.TUESDAY,
            ApcoaOpeningHoursWeekdays.WEDNESDAY,
            ApcoaOpeningHoursWeekdays.THURSDAY,
            ApcoaOpeningHoursWeekdays.FRIDAY,
            ApcoaOpeningHoursWeekdays.SATURDAY,
            ApcoaOpeningHoursWeekdays.SUNDAY,
        ]
        apcoa_opening_times = defaultdict(list)
        for opening_hours_input in apcoa_input.OpeningHours:
            opening_time = opening_hours_input.OpeningTimes if opening_hours_input.OpeningTimes != ApcoaOpeningHoursTime.CLOSED else 'off'
            if opening_hours_input.Weekday in apcoa_weekdays[:-2]:
                apcoa_opening_times[opening_time].append(opening_hours_input.Weekday.to_osm_opening_day_format())
        for opening_time, weekdays in apcoa_opening_times.items():
            if len(weekdays) == 7 and opening_time == apcoa_opening_times[ApcoaOpeningHoursTime.OPEN_24H]:
                static_parking_site_input.opening_hours = '24/7'
            elif (
                len(weekdays) == 5
                and ApcoaOpeningHoursWeekdays.SATURDAY not in weekdays
                and ApcoaOpeningHoursWeekdays.SUNDAY not in weekdays
            ):
                static_parking_site_input.opening_hours = f'Mo-Fr {opening_time}'
            else:
                static_parking_site_input.opening_hours = ';'.join([f'{weekday} {opening_time}' for weekday in weekdays])

        for capacity_data in apcoa_input.Spaces:
            # Because it was checked in validation, we can be sure that capacity will be set
            if capacity_data.Type == ApcoaParkingSpaceType.TOTAL_SPACES:
                static_parking_site_input.capacity = capacity_data.Count
            elif capacity_data.Type == ApcoaParkingSpaceType.DISABLED_SPACES:
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