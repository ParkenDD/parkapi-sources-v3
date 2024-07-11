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
    parkingFacilityCategory: Optional[str] = Noneable(StringValidator())
    parkingFacilityType: Optional[str] = Noneable(StringValidator())
    salesChannels: list[str] = ListValidator(StringValidator())
    operationTime: OpenDataSwissOperationTimeInput = DataclassValidator(OpenDataSwissOperationTimeInput)

    def __post_init__(self):
        for capacity in self.capacities:
            if capacity.categoryType == OpenDataSwissCapacityCategoryTypeInput.STANDARD:
                return
        # If no capacity with type PARKING was found, we miss the capacity and therefore throw a validation error
        raise ValidationError(reason='Missing parking spaces capacity')

    def get_osm_opening_hours(self) -> str:
        open_swiss_opening_times: dict[str, list[str]] = defaultdict(list)
        opening: list[str] = list(self.operationTime.operatingFrom.split(':'))
        closing: list[str] = list(self.operationTime.operatingTo.split(':'))
        opening_time: str = f'{opening[0]}:{opening[1]}-{closing[0]}:{closing[1]}'

        for day in self.operationTime.daysOfWeek:
            if opening_time == '00:00-00:00' or opening_time == '00:00-24:00':
                open_swiss_opening_times['24/7'].append('00:00-24:00')
            if day in list(OpenDataSwissOperationTimeDaysOfWeek)[:5]:
                open_swiss_opening_times['Mo-Fr'].append(opening_time)
            if day in list(OpenDataSwissOperationTimeDaysOfWeek):
                open_swiss_opening_times[day.value].append(opening_time)

        osm_opening_hour: list = []
        if len(open_swiss_opening_times['Mo-Fr']) == 5 and len(set(open_swiss_opening_times['Mo-Fr'])) == 1:
            osm_opening_hour.append(f'Mo-Fr {next(iter(set(open_swiss_opening_times["Mo-Fr"])))}')
        else:
            for weekday in list(OpenDataSwissOperationTimeDaysOfWeek)[:5]:
                if weekday.value in list(open_swiss_opening_times.keys()):
                    osm_opening_hour.append(f'{weekday.to_osm_opening_day_format()} {next(iter(open_swiss_opening_times[weekday.value]))}')
        if 'SATURDAY' in list(open_swiss_opening_times.keys()):
            days = OpenDataSwissOperationTimeDaysOfWeek.SATURDAY.to_osm_opening_day_format()
            osm_opening_hour.append(f'{days} {next(iter(open_swiss_opening_times["SATURDAY"]))}')
        if 'SUNDAY' in list(open_swiss_opening_times.keys()):
            days = OpenDataSwissOperationTimeDaysOfWeek.SUNDAY.to_osm_opening_day_format()
            osm_opening_hour.append(f'{days} {next(iter(open_swiss_opening_times["SUNDAY"]))}')
        osm_opening_hours = '; '.join(osm_opening_hour)
        if len(open_swiss_opening_times['24/7']) == 7:
            osm_opening_hours = '24/7'

        return osm_opening_hours


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
