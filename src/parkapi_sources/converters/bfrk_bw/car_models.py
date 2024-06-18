"""
Copyright 2024 binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

from enum import Enum

from validataclass.dataclasses import validataclass
from validataclass.validators import EnumValidator, IntegerValidator

from parkapi_sources.models import StaticParkingSiteInput
from parkapi_sources.models.enums import ParkingSiteType
from parkapi_sources.validators import ReplacingStringValidator

from .base_models import BfrkBaseRowInput


class BfrkCarType(Enum):
    PARK_AND_RIDE_PARKING_SITE = 'Park-and-Ride Parkplatz'
    SHORT_TERM_PARKING_SITE = 'Kurzzeitparkplätze'
    CAR_PARK = 'Parkhaus'
    DISABLED_PARKING_SPACE = 'Behindertenparkplatz'

    def to_parking_site_type(self) -> ParkingSiteType:
        return {
            self.PARK_AND_RIDE_PARKING_SITE: ParkingSiteType.OFF_STREET_PARKING_GROUND,
            self.SHORT_TERM_PARKING_SITE: ParkingSiteType.OFF_STREET_PARKING_GROUND,
            self.CAR_PARK: ParkingSiteType.CAR_PARK,
            self.DISABLED_PARKING_SPACE: ParkingSiteType.OTHER,
        }.get(self)


@validataclass
class BfrkCarRowInput(BfrkBaseRowInput):
    type: BfrkCarType = EnumValidator(BfrkCarType)
    capacity_disabled: int = IntegerValidator(allow_strings=True)
    description: str = ReplacingStringValidator(mapping={'\x80': '€'})

    def to_static_parking_site_input(self) -> StaticParkingSiteInput:
        static_parking_site_input = super().to_static_parking_site_input()

        static_parking_site_input.type = self.type.to_parking_site_type()
        static_parking_site_input.capacity_disabled = self.capacity_disabled
        static_parking_site_input.description = self.description

        return static_parking_site_input
