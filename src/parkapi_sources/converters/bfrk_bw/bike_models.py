"""
Copyright 2024 binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

from enum import Enum
from typing import Optional

from validataclass.dataclasses import Default, validataclass
from validataclass.validators import BooleanValidator, EnumValidator, IntegerValidator, StringValidator

from parkapi_sources.models.enums import ParkAndRideType, ParkingSiteType, PurposeType
from parkapi_sources.models.parking_site_inputs import StaticParkingSiteInput
from parkapi_sources.validators import EmptystringNoneable, ReplacingStringValidator

from .base_models import BfrkBaseInput


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
class BfrkBikeInput(BfrkBaseInput):
    anlagentyp: BfrkBikeType = EnumValidator(BfrkBikeType), Default(BfrkBikeType.OTHER)
    stellplatzanzahl: int = IntegerValidator()
    beleuchtet: Optional[bool] = BooleanValidator(), Default(None)
    ueberdacht: Optional[bool] = BooleanValidator(), Default(None)
    hinderniszufahrt: Optional[str] = EmptystringNoneable(StringValidator()), Default(None)
    kostenpflichtig: Optional[bool] = BooleanValidator(), Default(None)
    kostenpflichtignotiz: Optional[str] = (
        EmptystringNoneable(ReplacingStringValidator(mapping={'\x80': '€'})),
        Default(None),
    )
    notiz: Optional[str] = EmptystringNoneable(ReplacingStringValidator(mapping={'\x80': '€'})), Default(None)

    def to_static_parking_site_input(self) -> StaticParkingSiteInput:
        static_parking_site_input = StaticParkingSiteInput(
            type=self.anlagentyp.to_parking_site_type(),
            is_covered=self.ueberdacht,
            has_fee=self.kostenpflichtig,
            has_lighting=self.beleuchtet,
            purpose=PurposeType.BIKE,
            description=self.notiz,
            fee_description=self.kostenpflichtignotiz,
            park_and_ride_type=[ParkAndRideType.YES],
            capacity=self.stellplatzanzahl,
            **self.get_static_parking_site_input_kwargs(),
        )

        if self.kostenpflichtignotiz and 'bikeandridebox' in self.kostenpflichtignotiz:
            static_parking_site_input.has_fee = True

        return static_parking_site_input
