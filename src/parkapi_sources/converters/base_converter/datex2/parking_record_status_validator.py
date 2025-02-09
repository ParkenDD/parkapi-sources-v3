"""
Copyright 2025 binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

from datetime import datetime, timezone
from zoneinfo import ZoneInfo

from validataclass.dataclasses import validataclass
from validataclass.validators import DataclassValidator, DateTimeValidator, IntegerValidator, StringValidator

from parkapi_sources.models import RealtimeParkingSiteInput


@validataclass
class ParkingOccupancy:
    parkingNumberOfSpacesOverride: int = IntegerValidator(allow_strings=True)
    parkingNumberOfVacantSpaces: int = IntegerValidator(allow_strings=True)
    # parkingNumberOfOccupiedSpaces and parkingOccupancy are not needed


@validataclass
class ParkingRecordReference:
    id: str = StringValidator()


@validataclass
class ParkingRecordStatus:
    parkingOccupancy: ParkingOccupancy = DataclassValidator(ParkingOccupancy)
    parkingRecordReference: ParkingRecordReference = DataclassValidator(ParkingRecordReference)
    parkingStatusOriginTime: datetime = DateTimeValidator(
        local_timezone=ZoneInfo('Europe/Berlin'),
        target_timezone=timezone.utc,
    )

    def to_realtime_parking_site_input(self) -> RealtimeParkingSiteInput:
        return RealtimeParkingSiteInput(
            uid=self.parkingRecordReference.id.split('[')[0],
            realtime_capacity=self.parkingOccupancy.parkingNumberOfSpacesOverride,
            realtime_free_capacity=self.parkingOccupancy.parkingNumberOfVacantSpaces,
            realtime_data_updated_at=self.parkingStatusOriginTime,
        )
