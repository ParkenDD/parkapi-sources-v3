"""
Copyright 2024 binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

from datetime import datetime, timezone

import pyproj
from validataclass.dataclasses import validataclass
from validataclass.validators import DecimalValidator, IntegerValidator, StringValidator

from parkapi_sources.models import StaticParkingSiteInput
from parkapi_sources.models.enums import ParkingSiteType, PurposeType
from parkapi_sources.validators import PointCoordinateTupleValidator


@validataclass
class ReutlingenBikeRowInput:
    coordinates: list = PointCoordinateTupleValidator(DecimalValidator())
    capacity: int = IntegerValidator(allow_strings=True)
    name: str = StringValidator(max_length=255)
    additional_name: str = StringValidator(max_length=255)

    def to_parking_site_input(self, proj: pyproj.Proj) -> StaticParkingSiteInput:
        coordinates = proj(float(self.coordinates[0]), float(self.coordinates[1]), inverse=True)
        lat = coordinates[1]
        lon = coordinates[0]

        if self.name and self.additional_name:
            name = f'{self.name}, {self.additional_name}'
        elif self.additional_name:
            name = self.additional_name
        else:
            name = self.name
        return StaticParkingSiteInput(
            uid=f'{name}: {lat}-{lon}',
            lat=lat,
            lon=lon,
            name=name,
            static_data_updated_at=datetime.now(tz=timezone.utc),
            capacity=self.capacity,
            purpose=PurposeType.BIKE,
            type=ParkingSiteType.OTHER,
        )
