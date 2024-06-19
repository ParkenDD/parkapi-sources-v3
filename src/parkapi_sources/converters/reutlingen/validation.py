"""
Copyright 2024 binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

from datetime import datetime, timezone
from enum import Enum

from validataclass.dataclasses import validataclass
from validataclass.validators import DecimalValidator, EnumValidator, IntegerValidator, StringValidator

from parkapi_sources.models import StaticParkingSiteInput
from parkapi_sources.models.enums import ParkingSiteType
from parkapi_sources.validators import PointCoordinateTupleValidator


class ReutlingenParkingSiteType(Enum):
    PARKHAUS = 'parkhaus'
    TIEFGARAGE = 'tiefgarage'
    PARKFLAECHE = 'parkfläche'
    P_R = 'p+r'

    def to_parking_site_type_input(self) -> ParkingSiteType:
        return {
            self.PARKHAUS: ParkingSiteType.CAR_PARK,
            self.TIEFGARAGE: ParkingSiteType.UNDERGROUND,
            self.PARKFLAECHE: ParkingSiteType.OFF_STREET_PARKING_GROUND,
        }.get(self, ParkingSiteType.OTHER)


@validataclass
class ReutlingenRowInput:
    uid: int = IntegerValidator(allow_strings=True)
    type: ReutlingenParkingSiteType = EnumValidator(ReutlingenParkingSiteType)
    coordinates: list = PointCoordinateTupleValidator(DecimalValidator())
    capacity: int = IntegerValidator(allow_strings=True)
    name: str = StringValidator(max_length=255)

    def to_parking_site_input(self) -> StaticParkingSiteInput:
        return StaticParkingSiteInput(
            uid=str(self.uid),
            name=self.name,
            address=f'{self.name}, Reutlingen',
            lat=self.coordinates[1],
            lon=self.coordinates[0],
            type=self.type.to_parking_site_type_input(),
            capacity=self.capacity,
            static_data_updated_at=datetime.now(tz=timezone.utc),
        )
