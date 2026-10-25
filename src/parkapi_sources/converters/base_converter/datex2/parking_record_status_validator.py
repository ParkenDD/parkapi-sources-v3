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
    StringValidator,
)

from parkapi_sources.models import RealtimeParkingSiteInput
from parkapi_sources.models.enums import OpeningStatus


class ParkingSiteOpeningStatus(Enum):
    OPEN = 'open'
    CLOSED = 'closed'
    CLOSED_ABNORMAL = 'closedAbnormal'
    OPENING_TIMES_IN_FORCE = 'openingTimesInForce'
    STATUS_UNKNOWN = 'statusUnknown'
    OTHER = 'other'

    def to_opening_status(self) -> OpeningStatus | None:
        return {
            self.OPEN: OpeningStatus.OPEN,
            self.CLOSED: OpeningStatus.CLOSED,
            self.CLOSED_ABNORMAL: OpeningStatus.CLOSED,
            self.STATUS_UNKNOWN: OpeningStatus.UNKNOWN,
        }.get(self)


@validataclass
class ParkingOccupancy:
    parkingNumberOfSpacesOverride: int | None = IntegerValidator(allow_strings=True), Default(None)
    parkingNumberOfVacantSpaces: int | None = IntegerValidator(allow_strings=True), Default(None)
    parkingNumberOfOccupiedSpaces: int | None = IntegerValidator(allow_strings=True), Default(None)
    # parkingOccupancy is not needed


@validataclass
class ParkingRecordReference:
    id: str = StringValidator()


@validataclass
class ParkingRecordStatus:
    parkingOccupancy: ParkingOccupancy = DataclassValidator(ParkingOccupancy)
    parkingRecordReference: ParkingRecordReference = DataclassValidator(ParkingRecordReference)
    # parkingStatusOriginTime is set in some data sources, but not everywhere
    parkingStatusOriginTime: datetime | None = (
        DateTimeValidator(
            local_timezone=ZoneInfo('Europe/Berlin'),
            target_timezone=timezone.utc,
            discard_milliseconds=True,
        ),
        Default(None),
    )
    parkingSiteOpeningStatus: ParkingSiteOpeningStatus | None = (
        EnumValidator(ParkingSiteOpeningStatus),
        Default(None),
    )

    @property
    def uid(self) -> str:
        return self.parkingRecordReference.id.split('[')[0]

    def to_realtime_parking_site_input(self, static_capacity: int | None = None) -> RealtimeParkingSiteInput:
        """
        Some sources just publish the occupied spaces, so the free capacity has to be calculated with the total
        capacity. If the realtime data does not contain the total capacity, it can be given from the static data.
        """
        realtime_capacity = self.parkingOccupancy.parkingNumberOfSpacesOverride
        realtime_free_capacity = self.parkingOccupancy.parkingNumberOfVacantSpaces

        capacity = realtime_capacity if realtime_capacity is not None else static_capacity
        if (
            realtime_free_capacity is None
            and capacity is not None
            and self.parkingOccupancy.parkingNumberOfOccupiedSpaces is not None
        ):
            realtime_free_capacity = max(capacity - self.parkingOccupancy.parkingNumberOfOccupiedSpaces, 0)

        realtime_opening_status = None
        if self.parkingSiteOpeningStatus is not None:
            realtime_opening_status = self.parkingSiteOpeningStatus.to_opening_status()

        return RealtimeParkingSiteInput(
            uid=self.uid,
            realtime_capacity=realtime_capacity,
            realtime_free_capacity=realtime_free_capacity,
            realtime_opening_status=realtime_opening_status,
            realtime_data_updated_at=self.parkingStatusOriginTime or datetime.now(timezone.utc),
        )
