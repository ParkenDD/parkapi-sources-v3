"""
Copyright 2024 binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

from collections import defaultdict
from datetime import datetime, timezone
from enum import Enum
from typing import Optional

from validataclass.dataclasses import validataclass
from validataclass.exceptions import ValidationError
from validataclass.validators import DataclassValidator, EnumValidator, IntegerValidator, ListValidator, Noneable, StringValidator

from parkapi_sources.converters.base_converter.pull import GeojsonFeatureGeometryInput
from parkapi_sources.models import RealtimeParkingSiteInput, StaticParkingSiteInput
from parkapi_sources.models.enums import ParkAndRideType, ParkingSiteType, PurposeType


@validataclass
class OpenDataSwissAddressInput:
    addressLine: Optional[str] = Noneable(StringValidator())
    city: Optional[str] = Noneable(StringValidator())
    postalCode: Optional[str] = Noneable(StringValidator())


class OpenDataSwissCapacityCategoryTypeInput(Enum):
    STANDARD = 'STANDARD'
    DISABLED_PARKING_SPACE = 'DISABLED_PARKING_SPACE'
    RESERVABLE_PARKING_SPACE = 'RESERVABLE_PARKING_SPACE'
    WITH_CHARGING_STATION = 'WITH_CHARGING_STATION'


@validataclass
class OpenDataSwissCapacitiesInput:
    categoryType: OpenDataSwissCapacityCategoryTypeInput = EnumValidator(OpenDataSwissCapacityCategoryTypeInput)
    total: int = IntegerValidator()


@validataclass
class OpenDataSwissAdditionalInformationInput:
    de: Optional[str] = Noneable(StringValidator(multiline=False, unsafe=True))
    en: Optional[str] = Noneable(StringValidator(multiline=False, unsafe=True))
    it: Optional[str] = Noneable(StringValidator(multiline=False, unsafe=True))
    fr: Optional[str] = Noneable(StringValidator(multiline=False, unsafe=True))


class OpenDataSwissOperationTimeDaysOfWeek(Enum):
    MONDAY = 'MONDAY'
    TUESDAY = 'TUESDAY'
    WEDNESDAY = 'WEDNESDAY'
    THURSDAY = 'THURSDAY'
    FRIDAY = 'FRIDAY'
    SATURDAY = 'SATURDAY'
    SUNDAY = 'SUNDAY'

    def to_osm_opening_day_format(self) -> str:
        return {
            self.MONDAY: 'Mo',
            self.TUESDAY: 'Tu',
            self.WEDNESDAY: 'We',
            self.THURSDAY: 'Th',
            self.FRIDAY: 'Fr',
            self.SATURDAY: 'Sa',
            self.SUNDAY: 'Su',
        }.get(self, None)


@validataclass
class OpenDataSwissOperationTimeInput:
    operatingFrom: Optional[str] = Noneable(StringValidator())
    operatingTo: Optional[str] = Noneable(StringValidator())
    daysOfWeek: Optional[list[str]] = Noneable(ListValidator(EnumValidator(OpenDataSwissOperationTimeDaysOfWeek)))


@validataclass
class OpenDataSwissPropertiesInput:
    operator: str = StringValidator()
    displayName: str = StringValidator()
    address: Optional[OpenDataSwissAddressInput] = Noneable(DataclassValidator(OpenDataSwissAddressInput))
    capacities: list[OpenDataSwissCapacitiesInput] = ListValidator(DataclassValidator(OpenDataSwissCapacitiesInput))
    additionalInformationForCustomers: Optional[OpenDataSwissAdditionalInformationInput] = Noneable(
        DataclassValidator(OpenDataSwissAdditionalInformationInput)
    )
    parkingFacilityCategory: str = StringValidator()
    parkingFacilityType: Optional[str] = Noneable(StringValidator())
    salesChannels: Optional[list[str]] = Noneable(ListValidator(StringValidator()))
    operationTime: Optional[OpenDataSwissOperationTimeInput] = Noneable(DataclassValidator(OpenDataSwissOperationTimeInput))

    def __post_init__(self):
        for capacity in self.capacities:
            if capacity.categoryType == OpenDataSwissCapacityCategoryTypeInput.STANDARD:
                return
        # If no capacity with type PARKING was found, we miss the capacity and therefore throw a validation error
        raise ValidationError(reason='Missing parking spaces capacity')

    def get_osm_opening_hours(self) -> str:
        open_swiss_opening_times_by_weekday: dict[OpenDataSwissOperationTimeDaysOfWeek, list[str]] = defaultdict(list)
        check_counter_24_7: int = 0
        check_list_weekday: list[str] = []

        # OSM 24/7 has no secs in its timeformat and no endtime 00:00, so we replace with 24:00 and remove the secs
        closing_hh_mm_ss: list[str] = list(self.operationTime.operatingTo.replace('00:00:00', '24:00:00').split(':'))
        opening_hh_mm_ss: list[str] = list(self.operationTime.operatingFrom.split(':'))
        opening_time: str = f'{opening_hh_mm_ss[0]}:{opening_hh_mm_ss[1]}-{closing_hh_mm_ss[0]}:{closing_hh_mm_ss[1]}'

        for days_of_week_input in self.operationTime.daysOfWeek:
            # If it's open all day, add it to our 24/7 check counter, and we change opening_time to the OSM format
            if opening_time == '00:00-24:00':
                check_counter_24_7 += 1

            # Add opening times to fallback dict
            open_swiss_opening_times_by_weekday[days_of_week_input].append(opening_time)

            # If we have a weekday, add it to weekday list in order to check later if all weekdays have same data
            if days_of_week_input in list(OpenDataSwissOperationTimeDaysOfWeek)[:5]:
                check_list_weekday.append(opening_time)

        # If the check counter is 7, all weekdays are open at all time, which makes it 24/7. No further handling needed in this case.
        if check_counter_24_7 == 7:
            return '24/7'

        osm_opening_hour: list = []
        # If all Mo-Fr entries are the same, we can summarize it to the Mo-Fr entry, otherwise we have to set it separately
        if len(check_list_weekday) == 5 and len(set(check_list_weekday)) == 1:
            osm_opening_hour.append(f'Mo-Fr {check_list_weekday[0]}')
        else:
            for weekday in list(OpenDataSwissOperationTimeDaysOfWeek)[:5]:
                if weekday in list(open_swiss_opening_times_by_weekday):
                    osm_opening_hour.append(
                        f'{weekday.to_osm_opening_day_format()} {",".join(open_swiss_opening_times_by_weekday[weekday])}'
                    )

        # Weekends are handled separately
        for weekend_day in [OpenDataSwissOperationTimeDaysOfWeek.SATURDAY, OpenDataSwissOperationTimeDaysOfWeek.SUNDAY]:
            if weekend_day in list(open_swiss_opening_times_by_weekday):
                osm_opening_hour.append(
                    f'{weekend_day.to_osm_opening_day_format()} {",".join(open_swiss_opening_times_by_weekday[weekend_day])}'
                )

        return '; '.join(osm_opening_hour)


@validataclass
class OpenDataSwissFeatureInput:
    id: str = StringValidator()
    geometry: GeojsonFeatureGeometryInput = DataclassValidator(GeojsonFeatureGeometryInput)
    properties: OpenDataSwissPropertiesInput = DataclassValidator(OpenDataSwissPropertiesInput)

    def to_static_parking_site_input(self) -> StaticParkingSiteInput:
        static_parking_site_input = StaticParkingSiteInput(
            uid=str(self.id),
            name=self.properties.displayName,
            operator_name=self.properties.operator,
            lat=self.geometry.coordinates[1],
            lon=self.geometry.coordinates[0],
            static_data_updated_at=datetime.now(tz=timezone.utc),
            has_realtime_data=False,
        )

        if self.properties.parkingFacilityCategory == PurposeType.CAR:
            static_parking_site_input.purpose = PurposeType.CAR
            static_parking_site_input.type = ParkingSiteType.CAR_PARK
        elif self.properties.parkingFacilityCategory == PurposeType.BIKE:
            static_parking_site_input.purpose = PurposeType.BIKE
            static_parking_site_input.type = ParkingSiteType.OFF_STREET_PARKING_GROUND
        else:
            static_parking_site_input.purpose = PurposeType.CAR
            static_parking_site_input.type = ParkingSiteType.OTHER

        static_parking_site_input.opening_hours = self.properties.get_osm_opening_hours()

        if self.properties.additionalInformationForCustomers:
            static_parking_site_input.description = self.properties.additionalInformationForCustomers.de

        if (
            self.properties.address
            and self.properties.address.addressLine
            and self.properties.address.postalCode
            and self.properties.address.city
        ):
            static_parking_site_input.address = (
                f'{self.properties.address.addressLine}, {self.properties.address.postalCode} {self.properties.address.city}'
            )

        if self.properties.parkingFacilityType == 'PARK_AND_RAIL':
            static_parking_site_input.park_and_ride_type = [ParkAndRideType.TRAIN]

        for capacities_input in self.properties.capacities:
            if capacities_input.categoryType == OpenDataSwissCapacityCategoryTypeInput.STANDARD:
                static_parking_site_input.capacity = capacities_input.total
            elif capacities_input.categoryType == OpenDataSwissCapacityCategoryTypeInput.DISABLED_PARKING_SPACE:
                static_parking_site_input.capacity_disabled = capacities_input.total
            elif capacities_input.categoryType == OpenDataSwissCapacityCategoryTypeInput.WITH_CHARGING_STATION:
                static_parking_site_input.capacity_charging = capacities_input.total

        return static_parking_site_input

    def to_realtime_parking_site_input(self) -> Optional[RealtimeParkingSiteInput]:
        return None
