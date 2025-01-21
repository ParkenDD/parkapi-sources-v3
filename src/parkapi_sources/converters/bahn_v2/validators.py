"""
Copyright 2024 binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

from decimal import Decimal
from enum import Enum
from typing import Optional

from validataclass.dataclasses import Default, DefaultUnset, validataclass
from validataclass.exceptions import ValidationError
from validataclass.helpers import OptionalUnset
from validataclass.validators import (
    BooleanValidator,
    DataclassValidator,
    DecimalValidator,
    EnumValidator,
    IntegerValidator,
    ListValidator,
    Noneable,
    NoneToUnsetValue,
    NumericValidator,
    StringValidator,
    UrlValidator,
)

from parkapi_sources.models.enums import ParkingSiteType, PurposeType
from parkapi_sources.validators import MappedBooleanValidator


class NameContext(Enum):
    NAME = 'NAME'
    DISPLAY = 'DISPLAY'
    LABEL = 'LABEL'
    SLOGAN = 'SLOGAN'


class BahnParkingSiteCapacityType(Enum):
    PARKING = 'PARKING'
    HANDICAPPED_PARKING = 'HANDICAPPED_PARKING'
    BIKE_PARKING_LOCKED = 'BIKE_PARKING_LOCKED'
    BIKE_PARKING_OPEN = 'BIKE_PARKING_OPEN'


class BahnParkingSiteType(Enum):
    PARKPLATZ = 'Parkplatz'
    TIEFGARAGE = 'Tiefgarage'
    PARKHAUS = 'Parkhaus'
    STRASSE = 'Straße'
    PARKDECK = 'Parkdeck'

    def to_parking_site_type_input(self) -> ParkingSiteType:
        # TODO: find out more details about this enumeration for a proper mapping
        return {
            self.PARKPLATZ: ParkingSiteType.OFF_STREET_PARKING_GROUND,
            self.PARKHAUS: ParkingSiteType.CAR_PARK,
            self.TIEFGARAGE: ParkingSiteType.UNDERGROUND,
            self.STRASSE: ParkingSiteType.ON_STREET,
            self.PARKDECK: ParkingSiteType.CAR_PARK,
        }.get(self, ParkingSiteType.OTHER)


@validataclass
class BahnNameInput:
    name: str = StringValidator()
    context: NameContext = EnumValidator(NameContext)


@validataclass
class BahnTypeInput:
    name: BahnParkingSiteType = EnumValidator(BahnParkingSiteType)
    nameEn: str = StringValidator()
    abbreviation: str = StringValidator()


@validataclass
class BahnOperatorInput:
    name: str = StringValidator()
    # url: str = UrlValidator()  # TODO: urls are broken


@validataclass
class BahnLocationInput:
    longitude: Decimal = NumericValidator()
    latitude: Decimal = NumericValidator()


@validataclass
class BahnAdressInput:
    streetAndNumber: str = StringValidator()
    zip: str = StringValidator()
    city: str = StringValidator()
    phone: Optional[str] = Noneable(StringValidator())
    location: BahnLocationInput = DataclassValidator(BahnLocationInput)


@validataclass
class BahnStationIdInput:
    identifier: str = StringValidator()


@validataclass
class BahnStationInput:
    stationId: BahnStationIdInput = DataclassValidator(BahnStationIdInput)
    name: str = StringValidator()
    distance: str = StringValidator()


@validataclass
class BahnCapacityInput:
    type: BahnParkingSiteCapacityType = EnumValidator(BahnParkingSiteCapacityType)
    available: OptionalUnset[bool] = (
        NoneToUnsetValue(MappedBooleanValidator(mapping={'true': True, 'false': False})),
        DefaultUnset,
    )
    total: int = IntegerValidator(allow_strings=True, min_value=0)

    def to_bike_parking_site_type_input(self) -> ParkingSiteType:
        # TODO: find out more details about this enumeration for a proper mapping
        if self.available and self.type == BahnParkingSiteCapacityType.BIKE_PARKING_LOCKED:
            return ParkingSiteType.LOCKBOX
        return ParkingSiteType.OTHER

    def to_purpose_type_input(self) -> PurposeType:
        if self.type in [
            BahnParkingSiteCapacityType.BIKE_PARKING_LOCKED,
            BahnParkingSiteCapacityType.BIKE_PARKING_OPEN,
        ]:
            return PurposeType.BIKE
        return PurposeType.CAR


@validataclass
class BahnOpeningHoursInput:
    text: Optional[str] = StringValidator(), Default(None)
    is24h: bool = BooleanValidator()


@validataclass
class BahnClearanceInput:
    height: Optional[Decimal] = Noneable(DecimalValidator()), Default(None)
    width: Optional[Decimal] = Noneable(DecimalValidator()), Default(None)


@validataclass
class BahnRestrictionInput:
    clearance: BahnClearanceInput = DataclassValidator(BahnClearanceInput)


@validataclass
class BahnAccessInput:
    openingHours: BahnOpeningHoursInput = DataclassValidator(BahnOpeningHoursInput)
    restrictions: BahnRestrictionInput = DataclassValidator(BahnRestrictionInput)
    # TODO: ignored multiple attributes which do not matter so far


@validataclass
class BahnParkingSiteInput:
    id: int = IntegerValidator(allow_strings=True)
    name: list[BahnNameInput] = ListValidator(DataclassValidator(BahnNameInput))
    url: Optional[str] = UrlValidator(), Default(None)
    type: BahnTypeInput = DataclassValidator(BahnTypeInput)
    operator: BahnOperatorInput = DataclassValidator(BahnOperatorInput)
    address: BahnAdressInput = DataclassValidator(BahnAdressInput)
    capacity: list[BahnCapacityInput] = ListValidator(DataclassValidator(BahnCapacityInput))
    access: BahnAccessInput = DataclassValidator(BahnAccessInput)

    def __post_init__(self):
        for capacity in self.capacity:
            if capacity.type == BahnParkingSiteCapacityType.PARKING:
                return
        # If no capacity with type PARKING was found, we miss the capacity and therefore throw a validation error
        raise ValidationError(reason='Missing parking capacity')

    def get_capacity_by_type(self, capacity_type: BahnParkingSiteCapacityType) -> BahnCapacityInput | None:
        for capacity in self.capacity:
            if capacity.type == capacity_type:
                return capacity

    def get_name(self) -> str:
        for name_input in self.name:
            if name_input.context == NameContext.NAME:
                return name_input.name
        return ''
