"""
Copyright 2026 binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

from datetime import datetime
from decimal import Decimal

from validataclass.dataclasses import validataclass
from validataclass.validators import DataclassValidator, IntegerValidator, NumericValidator, StringValidator

from parkapi_sources.models import RealtimeParkingSiteInput, StaticParkingSiteInput
from parkapi_sources.models.enums import ParkingSiteType, PurposeType
from parkapi_sources.util import round_7d


@validataclass
class EllwangenSensitActualStatusInput:
    parkingCapacity: int = IntegerValidator(min_value=0, allow_strings=True)
    vacantSpaces: int = IntegerValidator(min_value=0, allow_strings=True)


@validataclass
class EllwangenSensitLocationInput:
    latitude: Decimal = NumericValidator()
    longitude: Decimal = NumericValidator()


@validataclass
class EllwangenSensitParkingLotInput:
    id: str = StringValidator(min_length=1, max_length=256)
    name: str = StringValidator(min_length=1, max_length=256)
    actualStatus: EllwangenSensitActualStatusInput = DataclassValidator(EllwangenSensitActualStatusInput)
    location: EllwangenSensitLocationInput = DataclassValidator(EllwangenSensitLocationInput)

    def to_static_parking_site_input(self, static_data_updated_at: datetime) -> StaticParkingSiteInput:
        return StaticParkingSiteInput(
            uid=self.id,
            name=self.name,
            type=ParkingSiteType.OFF_STREET_PARKING_GROUND,
            purpose=PurposeType.CAR,
            capacity=self.actualStatus.parkingCapacity,
            lat=round_7d(self.location.latitude),
            lon=round_7d(self.location.longitude),
            has_realtime_data=True,
            static_data_updated_at=static_data_updated_at,
        )

    def to_realtime_parking_site_input(self, realtime_data_updated_at: datetime) -> RealtimeParkingSiteInput:
        return RealtimeParkingSiteInput(
            uid=self.id,
            realtime_capacity=self.actualStatus.parkingCapacity,
            realtime_free_capacity=self.actualStatus.vacantSpaces,
            realtime_data_updated_at=realtime_data_updated_at,
        )
