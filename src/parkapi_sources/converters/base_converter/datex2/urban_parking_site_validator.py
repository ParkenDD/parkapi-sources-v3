"""
Copyright 2025 binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

from datetime import datetime
from decimal import Decimal
from enum import Enum

from validataclass.dataclasses import Default, validataclass
from validataclass.validators import (
    DataclassValidator,
    DateTimeValidator,
    DecimalValidator,
    EnumValidator,
    IntegerValidator,
    ListValidator,
    StringValidator,
)

from parkapi_sources.models import StaticParkingSiteInput
from parkapi_sources.models.enums import ParkingAudience, ParkingSiteType, PurposeType


class ParkingLayout(Enum):
    MULTI_STOREY = 'multiStorey'
    SINGLE_LEVEL = 'singleLevel'
    UNDERGROUND = 'underground'
    UNDERGROUND_AND_MULTI_STOREY = 'undergroundAndMultiStorey'
    AUTOMATED_PARKING_GARAGE = 'automatedParkingGarage'
    OPEN_SPACE = 'openSpace'
    COVERED = 'covered'
    NESTED = 'nested'
    FIELD = 'field'
    UNKNOWN = 'unknown'
    OTHER = 'other'

    def to_parking_site_type(self) -> ParkingSiteType | None:
        return {
            self.UNDERGROUND: ParkingSiteType.UNDERGROUND,
            self.UNDERGROUND_AND_MULTI_STOREY: ParkingSiteType.CAR_PARK,
            self.AUTOMATED_PARKING_GARAGE: ParkingSiteType.CAR_PARK,
            self.MULTI_STOREY: ParkingSiteType.CAR_PARK,
            self.SINGLE_LEVEL: ParkingSiteType.OFF_STREET_PARKING_GROUND,
            self.COVERED: ParkingSiteType.OFF_STREET_PARKING_GROUND,
            self.FIELD: ParkingSiteType.OFF_STREET_PARKING_GROUND,
        }.get(self)


class Language(Enum):
    DE = 'de'


class ApplicableForUser(Enum):
    DISABLED = 'disabled'

    def to_parking_audience(self) -> ParkingAudience | None:
        return {
            self.DISABLED: ParkingAudience.DISABLED,
        }.get(self)


class DatexUrbanParkingSiteType(Enum):
    ON_STREET_PARKING = 'onStreetParking'
    OFF_STREET_PARKING = 'offStreetParking'
    OTHER = 'other'

    def to_parking_site_type(self) -> ParkingSiteType | None:
        return {
            self.OFF_STREET_PARKING: ParkingSiteType.OFF_STREET_PARKING_GROUND,
            self.ON_STREET_PARKING: ParkingSiteType.ON_STREET,
        }.get(self)


@validataclass
class PointCoordinates:
    latitude: Decimal = DecimalValidator()
    longitude: Decimal = DecimalValidator()


@validataclass
class PointByCoordinates:
    pointCoordinates: PointCoordinates = DataclassValidator(PointCoordinates)


@validataclass
class ParkingLocation:
    pointByCoordinates: PointByCoordinates = DataclassValidator(PointByCoordinates)


@validataclass
class ParkingName:
    _text: str = StringValidator()
    lang: Language = EnumValidator(Language)


@validataclass
class AssignedParking:
    applicableForUser: list[ApplicableForUser] = ListValidator(EnumValidator(ApplicableForUser))


@validataclass
class UrbanParkingSite:
    id: str = StringValidator()
    parkingLayout: ParkingLayout = EnumValidator(ParkingLayout)
    parkingLocation: ParkingLocation = DataclassValidator(ParkingLocation)
    parkingName: list[ParkingName] = ListValidator(DataclassValidator(ParkingName))
    parkingNumberOfSpaces: int = IntegerValidator(allow_strings=True)
    parkingRecordVersionTime: datetime = DateTimeValidator(discard_milliseconds=True)
    assignedParkingAmongOthers: AssignedParking | None = DataclassValidator(AssignedParking), Default(None)
    urbanParkingSiteType: DatexUrbanParkingSiteType = EnumValidator(DatexUrbanParkingSiteType)

    def to_static_parking_site_input(self, has_realtime_data: bool) -> StaticParkingSiteInput:
        name_de = ''
        for name in self.parkingName:
            if name.lang == Language.DE:
                name_de = name._text

        if self.urbanParkingSiteType.to_parking_site_type() == ParkingSiteType.ON_STREET:
            parking_site_type = ParkingSiteType.ON_STREET
        else:
            parking_site_type = self.parkingLayout.to_parking_site_type()
            if parking_site_type is None:
                parking_site_type = self.urbanParkingSiteType.to_parking_site_type()
            if parking_site_type is None:
                parking_site_type = ParkingSiteType.OTHER

        static_parking_site_input = StaticParkingSiteInput(
            uid=self.id,
            name=name_de,
            purpose=PurposeType.CAR,
            type=parking_site_type,
            lat=self.parkingLocation.pointByCoordinates.pointCoordinates.latitude,
            lon=self.parkingLocation.pointByCoordinates.pointCoordinates.longitude,
            capacity=self.parkingNumberOfSpaces,
            static_data_updated_at=self.parkingRecordVersionTime,
            has_realtime_data=has_realtime_data,
        )

        if self.parkingLayout == ParkingLayout.COVERED:
            static_parking_site_input.is_covered = True

        return static_parking_site_input
