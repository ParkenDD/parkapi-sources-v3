"""
Copyright 2025 binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

from datetime import datetime
from decimal import Decimal
from enum import Enum

from validataclass.dataclasses import Default, validataclass
from validataclass.validators import (
    AnythingValidator,
    DataclassValidator,
    DateTimeValidator,
    DecimalValidator,
    EnumValidator,
    IntegerValidator,
    ListValidator,
    Noneable,
    StringValidator,
)

from parkapi_sources.models import StaticParkingSiteInput
from parkapi_sources.models.enums import ParkingSiteType, PurposeType
from parkapi_sources.validators import MappedBooleanValidator


class InterUrbanParkingSiteLocation(Enum):
    MOTORWAY = 'motorway'
    OTHER = 'other'

    def to_parking_site_type(self) -> ParkingSiteType | None:
        return {
            self.MOTORWAY: ParkingSiteType.OFF_STREET_PARKING_GROUND,
        }.get(self)


class Language(Enum):
    DE = 'de'


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
class LocalisedValue:
    _text: str = StringValidator()
    lang: Language | None = Noneable(EnumValidator(Language)), Default(None)


@validataclass
class LocalisedName:
    values: LocalisedValue = DataclassValidator(LocalisedValue)


@validataclass
class ParkingSiteAddress:
    contactDetailsStreet: str | None = Noneable(StringValidator()), Default(None)
    # contactDetailsHouseNumber is a single string or, when split into multiple tags (e.g. "n/a"), a list of strings
    contactDetailsHouseNumber: list | str | None = (
        Noneable(AnythingValidator(allowed_types=[list, str])),
        Default(None),
    )
    contactDetailsPostcode: str | None = Noneable(StringValidator()), Default(None)
    contactDetailsCity: LocalisedName | None = Noneable(DataclassValidator(LocalisedName)), Default(None)


@validataclass
class TariffsAndPayment:
    freeOfCharge: bool | None = MappedBooleanValidator(mapping={'true': True, 'false': False}), Default(None)


@validataclass
class InterUrbanParkingSite:
    id: str = StringValidator()
    parkingLocation: ParkingLocation = DataclassValidator(ParkingLocation)
    parkingName: list[ParkingName] = ListValidator(DataclassValidator(ParkingName))
    parkingNumberOfSpaces: int = IntegerValidator(allow_strings=True)
    parkingRecordVersionTime: datetime = DateTimeValidator(discard_milliseconds=True)
    interUrbanParkingSiteLocation: InterUrbanParkingSiteLocation | None = (
        EnumValidator(InterUrbanParkingSiteLocation),
        Default(None),
    )
    tariffsAndPayment: TariffsAndPayment | None = DataclassValidator(TariffsAndPayment), Default(None)
    parkingSiteAddress: ParkingSiteAddress | None = Noneable(DataclassValidator(ParkingSiteAddress)), Default(None)

    def to_static_parking_site_input(self, has_realtime_data: bool) -> StaticParkingSiteInput | None:
        # Parking sites without any spaces are ignored
        if self.parkingNumberOfSpaces == 0:
            return None

        name_de = ''
        for name in self.parkingName:
            if name.lang == Language.DE:
                name_de = name._text

        parking_site_type = None
        if self.interUrbanParkingSiteLocation is not None:
            parking_site_type = self.interUrbanParkingSiteLocation.to_parking_site_type()
        if parking_site_type is None:
            parking_site_type = ParkingSiteType.OFF_STREET_PARKING_GROUND

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

        if self.tariffsAndPayment is not None and self.tariffsAndPayment.freeOfCharge is not None:
            static_parking_site_input.has_fee = not self.tariffsAndPayment.freeOfCharge

        address = self._get_address()
        if address is not None:
            static_parking_site_input.address = address

        return static_parking_site_input

    def _get_address(self) -> str | None:
        if self.parkingSiteAddress is None:
            return None

        house_number = self.parkingSiteAddress.contactDetailsHouseNumber
        if isinstance(house_number, list):
            house_number = ''.join(house_number)

        city = None
        if self.parkingSiteAddress.contactDetailsCity is not None:
            city = self.parkingSiteAddress.contactDetailsCity.values._text

        # Address components containing "n/a" are treated as missing
        street_line = ' '.join(
            component
            for component in [self.parkingSiteAddress.contactDetailsStreet, house_number]
            if self._is_valid_address_component(component)
        )
        city_line = ' '.join(
            component
            for component in [self.parkingSiteAddress.contactDetailsPostcode, city]
            if self._is_valid_address_component(component)
        )
        address = ', '.join(line for line in [street_line, city_line] if line)

        return address or None

    @staticmethod
    def _is_valid_address_component(component: str | None) -> bool:
        return bool(component) and 'n/a' not in component.lower()
