"""
Copyright 2025 binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

from datetime import datetime, timezone
from enum import Enum
from zoneinfo import ZoneInfo

from validataclass.dataclasses import Default, validataclass
from validataclass.validators import (
    DataclassValidator,
    DateTimeValidator,
    EnumValidator,
    IntegerValidator,
    Noneable,
    StringValidator,
)

from parkapi_sources.models import RealtimeParkingSiteInput
from parkapi_sources.models.enums import OpeningStatus


class ParkingSiteOpeningStatus(Enum):
    OPEN = 'open'
    CLOSED = 'closed'
    OTHER = 'other'

    def to_opening_status(self) -> OpeningStatus:
        return {
            self.OPEN: OpeningStatus.OPEN,
            self.CLOSED: OpeningStatus.CLOSED,
        }.get(self, OpeningStatus.UNKNOWN)


@validataclass
class ParkingRecordReference:
    id: str = StringValidator()


@validataclass
class ParkingOccupancy:
    # parkingNumberOfVehicles is the number of occupied spaces
    parkingNumberOfVehicles: int | None = Noneable(IntegerValidator(allow_strings=True)), Default(None)


@validataclass
class TollCollectParkingRecordStatus:
    parkingRecordReference: ParkingRecordReference = DataclassValidator(ParkingRecordReference)
    parkingStatusOriginTime: datetime | None = (
        DateTimeValidator(
            local_timezone=ZoneInfo('Europe/Berlin'),
            target_timezone=timezone.utc,
            discard_milliseconds=True,
        ),
        Default(None),
    )
    parkingOccupancy: ParkingOccupancy | None = Noneable(DataclassValidator(ParkingOccupancy)), Default(None)
    parkingSiteOpeningStatus: ParkingSiteOpeningStatus | None = (
        EnumValidator(ParkingSiteOpeningStatus),
        Default(None),
    )

    @property
    def uid(self) -> str:
        return self.parkingRecordReference.id.split('[')[0]

    def to_realtime_parking_site_input(self, capacity: int | None) -> RealtimeParkingSiteInput:
        occupied_spaces = None
        if self.parkingOccupancy is not None:
            occupied_spaces = self.parkingOccupancy.parkingNumberOfVehicles

        # The realtime data only provides the number of occupied spaces. We calculate the free capacity by subtracting
        # it from the static total capacity, which is fetched alongside the realtime data.
        realtime_free_capacity = None
        if capacity is not None and occupied_spaces is not None:
            realtime_free_capacity = max(capacity - occupied_spaces, 0)

        realtime_opening_status = None
        if self.parkingSiteOpeningStatus is not None:
            realtime_opening_status = self.parkingSiteOpeningStatus.to_opening_status()

        return RealtimeParkingSiteInput(
            uid=self.uid,
            realtime_capacity=capacity,
            realtime_free_capacity=realtime_free_capacity,
            realtime_opening_status=realtime_opening_status,
            realtime_data_updated_at=self.parkingStatusOriginTime or datetime.now(timezone.utc),
        )
