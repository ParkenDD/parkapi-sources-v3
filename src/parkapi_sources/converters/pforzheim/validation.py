"""
Copyright 2024 binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

from decimal import Decimal
from enum import Enum
from typing import Optional

from validataclass.dataclasses import validataclass
from validataclass.validators import EnumValidator, IntegerValidator, NumericValidator, StringValidator

from parkapi_sources.models.enums import ParkingSiteType
from parkapi_sources.validators import ExcelNoneable, MappedBooleanValidator, ReplacingStringValidator


class PforzheimParkingSiteType(Enum):
    CARPARK = 'carPark'
    UNDERGROUNDCARPARK = 'undergroundCarPark'

    def to_parking_site_type_input(self) -> ParkingSiteType:
        return {
            self.CARPARK: ParkingSiteType.CAR_PARK,
            self.UNDERGROUNDCARPARK: ParkingSiteType.UNDERGROUND,
        }.get(self, ParkingSiteType.OTHER)


@validataclass
class PforzheimInput:
    Id: str = StringValidator(max_length=255)
    name: str = StringValidator(max_length=255)
    operatorID: str = StringValidator(max_length=255)
    address: str = ReplacingStringValidator(max_length=255, mapping={'\n': ' '})
    description: str = ReplacingStringValidator(max_length=512, mapping={'\n': ' '})
    type: PforzheimParkingSiteType = EnumValidator(PforzheimParkingSiteType)
    lat: Decimal = NumericValidator(min_value=40, max_value=60)
    lon: Decimal = NumericValidator(min_value=7, max_value=10)
    capacity: int = IntegerValidator()
    quantitySpacesReservedForWomen: Optional[int] = ExcelNoneable(IntegerValidator())
    quantitySpacesReservedForMobilityImpededPerson: Optional[int] = ExcelNoneable(IntegerValidator())
    securityInformation: str = ReplacingStringValidator(mapping={'\n': ' '})
    feeInformation: str = ReplacingStringValidator(mapping={'\n': ' '})
    hasOpeningHours24h: bool = MappedBooleanValidator(mapping={'wahr': True, 'falsch': False})
