"""
Copyright 2025 binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

from datetime import datetime

from validataclass.dataclasses import validataclass
from validataclass.validators import DecimalValidator, IntegerValidator, StringValidator

from parkapi_sources.models import StaticParkingSpotInput
from parkapi_sources.models.enums import PurposeType
from parkapi_sources.validators import PointCoordinateTupleValidator


@validataclass
class ReutlingenDisabledRowInput:
    uid: int = IntegerValidator(allow_strings=True)
    coordinates: list = PointCoordinateTupleValidator(DecimalValidator())
    name: str = StringValidator(max_length=255)

    def to_parking_spot_input(self, static_data_updated_at: datetime) -> StaticParkingSpotInput:
        return StaticParkingSpotInput(
            uid=str(self.uid),
            lat=self.coordinates[1],
            lon=self.coordinates[0],
            name=self.name,
            address=f'{self.name.replace("gegenüber", "").strip()}, Reutlingen',
            static_data_updated_at=static_data_updated_at,
            purpose=PurposeType.CAR,
            has_realtime_data=False,
        )
