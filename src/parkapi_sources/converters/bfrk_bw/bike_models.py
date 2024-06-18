"""
Copyright 2024 binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

from enum import Enum
from typing import Optional

from validataclass.dataclasses import validataclass
from validataclass.validators import EnumValidator

from parkapi_sources.models.enums import ParkingSiteType, PurposeType
from parkapi_sources.models.parking_site_inputs import StaticParkingSiteInput
from parkapi_sources.validators import ExcelNoneable, MappedBooleanValidator

from .base_models import BfrkBaseRowInput


class GermanMappedBooleanValidator(MappedBooleanValidator):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, mapping={'ja': True, 'nein': False}, **kwargs)


class BfrkBikeType(Enum):
    WALL_LOOPS = 'Vorderradhalter'
    STANDS = 'Anlehnbuegel'
    LOCKERS = 'Fahrradboxen'
    TWO_TIER = 'doppelstoeckig'
    SHED = 'Fahrradsammelanlage'
    BUILDING = 'Fahrradparkhaus'
    AUTOMATIC_BUILDING = 'automatischesParksystem'
    OTHER = 'Sonstiges'

    def to_parking_site_type(self) -> ParkingSiteType:
        if self == BfrkBikeType.AUTOMATIC_BUILDING:
            return ParkingSiteType.BUILDING
        return ParkingSiteType[self.name]


@validataclass
class BfrkBikeRowInput(BfrkBaseRowInput):
    type: BfrkBikeType = EnumValidator(BfrkBikeType)
    has_roof: Optional[bool] = ExcelNoneable(GermanMappedBooleanValidator())
    has_fee: bool = GermanMappedBooleanValidator()
    has_lighting: bool = GermanMappedBooleanValidator()

    def to_static_parking_site_input(self) -> StaticParkingSiteInput:
        static_parking_site_input = super().to_static_parking_site_input()

        static_parking_site_input.type = self.type.to_parking_site_type()
        static_parking_site_input.has_roof = self.has_roof
        static_parking_site_input.has_fee = self.has_fee
        static_parking_site_input.has_lighting = self.has_lighting
        static_parking_site_input.purpose = PurposeType.BIKE

        return static_parking_site_input
