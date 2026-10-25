"""
Copyright 2026 binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

from datetime import datetime, timezone
from zoneinfo import ZoneInfo

from validataclass.dataclasses import Default, validataclass
from validataclass.validators import DataclassValidator, DateTimeValidator, IntegerValidator, StringValidator

from parkapi_sources.models import RealtimeParkingSiteInput


@validataclass
class ParkingOccupancy:
    parkingNumberOfVacantSpaces: int = IntegerValidator(allow_strings=True)
    # parkingOccupancy and parkingOccupancyGraded are not needed


@validataclass
class ParkingRecordReference:
    id: str = StringValidator()


@validataclass
class ParkingRecordStatus:
    parkingRecordReference: ParkingRecordReference = DataclassValidator(ParkingRecordReference)
    parkingOccupancy: ParkingOccupancy = DataclassValidator(ParkingOccupancy)
    parkingStatusOriginTime: datetime | None = (
        DateTimeValidator(
            local_timezone=ZoneInfo('Europe/Berlin'),
            target_timezone=timezone.utc,
            discard_milliseconds=True,
        ),
        Default(None),
    )

    def to_realtime_parking_site_input(self) -> RealtimeParkingSiteInput:
        return RealtimeParkingSiteInput(
            uid=self.parkingRecordReference.id,
            realtime_free_capacity=self.parkingOccupancy.parkingNumberOfVacantSpaces,
            realtime_data_updated_at=self.parkingStatusOriginTime or datetime.now(timezone.utc),
        )
