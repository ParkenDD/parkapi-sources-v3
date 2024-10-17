"""
Copyright 2024 binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

from enum import Enum
from typing import Optional

from validataclass.dataclasses import Default, validataclass
from validataclass.validators import EnumValidator, IntegerValidator, StringValidator

from parkapi_sources.models import StaticParkingSiteInput
from parkapi_sources.models.enums import ParkAndRideType, ParkingSiteType
from parkapi_sources.validators import EmptystringNoneable, ReplacingStringValidator

from .base_models import BfrkBaseInput


class BfrkCarType(Enum):
    PARK_AND_RIDE_PARKING_SITE = 'Park+Ride'
    SHORT_TERM_PARKING_SITE = 'Kurzzeit'
    CAR_PARK = 'Parkhaus'
    DISABLED_PARKING_SPACE = 'Behindertenplätze'
    OFF_STREET_PARKING_GROUND = 'Parkplatz'
    OFF_STREET_PARKING_GROUND_2 = 'Parkplatz_ohne_Park+Ride'

    def to_parking_site_type(self) -> ParkingSiteType:
        return {
            self.PARK_AND_RIDE_PARKING_SITE: ParkingSiteType.OFF_STREET_PARKING_GROUND,
            self.SHORT_TERM_PARKING_SITE: ParkingSiteType.OFF_STREET_PARKING_GROUND,
            self.CAR_PARK: ParkingSiteType.CAR_PARK,
            self.DISABLED_PARKING_SPACE: ParkingSiteType.OTHER,
            self.OFF_STREET_PARKING_GROUND: ParkingSiteType.OFF_STREET_PARKING_GROUND,
            self.OFF_STREET_PARKING_GROUND_2: ParkingSiteType.OFF_STREET_PARKING_GROUND,
        }.get(self)


@validataclass
class BfrkCarInput(BfrkBaseInput):
    art: BfrkCarType = EnumValidator(BfrkCarType), Default(BfrkCarType.OFF_STREET_PARKING_GROUND)
    stellplaetzegesamt: int = IntegerValidator()
    behindertenstellplaetze: Optional[int] = IntegerValidator(), Default(None)
    bedingungen: Optional[str] = EmptystringNoneable(ReplacingStringValidator(mapping={'\x80': '€'})), Default(None)
    eigentuemer: Optional[str] = EmptystringNoneable(StringValidator()), Default(None)

    def to_static_parking_site_input(self) -> StaticParkingSiteInput:
        static_parking_site_input = StaticParkingSiteInput(
            type=self.art.to_parking_site_type(),
            capacity=self.stellplaetzegesamt,
            capacity_disabled=self.behindertenstellplaetze,
            description=self.bedingungen,
            operator_name=self.eigentuemer,
            **self.get_static_parking_site_input_kwargs(),
        )

        if self.art == BfrkCarType.PARK_AND_RIDE_PARKING_SITE:
            static_parking_site_input.park_and_ride_type = [ParkAndRideType.YES]

        return static_parking_site_input
