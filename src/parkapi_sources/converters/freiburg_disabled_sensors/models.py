"""
Copyright 2025 binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

from datetime import datetime, timezone
from enum import Enum

from validataclass.dataclasses import validataclass
from validataclass.validators import DataclassValidator, EnumValidator, RegexValidator, StringValidator

from parkapi_sources.models import (
    GeojsonBaseFeatureInput,
    ParkingSpotRestrictionInput,
    RealtimeParkingSpotInput,
    StaticParkingSpotInput,
)
from parkapi_sources.models.enums import ParkingAudience, ParkingSpotStatus, PurposeType
from parkapi_sources.util import round_7d


class FreiburgDisabledStatus(Enum):
    AVAILABLE = 0
    TAKEN = 1

    def to_status(self) -> ParkingSpotStatus:
        return {
            self.AVAILABLE: ParkingSpotStatus.AVAILABLE,
            self.TAKEN: ParkingSpotStatus.TAKEN,
        }.get(self)


@validataclass
class FreiburgDisabledSensorsPropertiesInput:
    name: str = RegexValidator(pattern=r'^.* - .*$')  # We expect 'short name - name'
    adresse: str = StringValidator()
    status: FreiburgDisabledStatus = EnumValidator(FreiburgDisabledStatus)


@validataclass
class FreiburgDisabledSensorFeatureInput(GeojsonBaseFeatureInput):
    properties: FreiburgDisabledSensorsPropertiesInput = DataclassValidator(FreiburgDisabledSensorsPropertiesInput)

    def to_static_parking_spot_input(self) -> StaticParkingSpotInput:
        return StaticParkingSpotInput(
            uid=self.properties.name.split(' - ')[0],
            name=self.properties.name,
            address=None if self.properties.adresse == '' else self.properties.adresse.replace(', Germany', ''),
            static_data_updated_at=datetime.now(tz=timezone.utc),
            lat=round_7d(self.geometry.y),
            lon=round_7d(self.geometry.x),
            has_realtime_data=True,
            restrictions=[ParkingSpotRestrictionInput(type=ParkingAudience.DISABLED)],
            purpose=PurposeType.CAR,
        )

    def to_realtime_parking_spot_input(self) -> RealtimeParkingSpotInput:
        return RealtimeParkingSpotInput(
            uid=self.properties.name.split(' - ')[0],
            realtime_status=self.properties.status.to_status(),
            realtime_data_updated_at=datetime.now(tz=timezone.utc),
        )
