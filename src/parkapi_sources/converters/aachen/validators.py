"""
Copyright 2025 binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

from datetime import datetime
from decimal import Decimal
from enum import Enum

from validataclass.dataclasses import validataclass
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
from parkapi_sources.models.enums import ParkingSiteType, PurposeType


class ParkingLayout(Enum):
    MULTI_STOREY = 'multiStorey'


class Language(Enum):
    DE = 'de'


class DatexUrbanParkingSiteType(Enum):
    OFF_STREET_PARKING = 'offStreetParking'

    def to_parking_site_type(self) -> ParkingSiteType:
        return {
            self.OFF_STREET_PARKING: ParkingSiteType.OFF_STREET_PARKING_GROUND,
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
class ParkingRecord:
    id: str = StringValidator()
    parkingLayout: ParkingLayout = EnumValidator(ParkingLayout)
    parkingLocation: ParkingLocation = DataclassValidator(ParkingLocation)
    parkingName: list[ParkingName] = ListValidator(DataclassValidator(ParkingName))
    parkingNumberOfSpaces: int = IntegerValidator(allow_strings=True)
    parkingRecordVersionTime: datetime = DateTimeValidator()
    urbanParkingSiteType: DatexUrbanParkingSiteType = EnumValidator(DatexUrbanParkingSiteType)

    def to_static_parking_site_input(self) -> StaticParkingSiteInput:
        name_de = ''
        for name in self.parkingName:
            if name.lang == Language.DE:
                name_de = name._text

        return StaticParkingSiteInput(
            uid=self.id,
            name=name_de,
            purpose=PurposeType.CAR,
            type=self.urbanParkingSiteType.to_parking_site_type(),
            lat=self.parkingLocation.pointByCoordinates.pointCoordinates.latitude,
            lon=self.parkingLocation.pointByCoordinates.pointCoordinates.longitude,
            capacity=self.parkingNumberOfSpaces,
            static_data_updated_at=self.parkingRecordVersionTime,
        )
