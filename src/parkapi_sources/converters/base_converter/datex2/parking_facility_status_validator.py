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
    ListValidator,
    StringValidator,
)

from parkapi_sources.models import RealtimeParkingSiteInput
from parkapi_sources.models.enums import OpeningStatus


class ParkingFacilityStatusType(Enum):
    OPEN = 'open'
    CLOSED = 'closed'
    SPACES_AVAILABLE = 'spacesAvailable'
    ALMOST_FULL = 'almostFull'
    FULL_AT_ENTRANCE = 'fullAtEntrance'
    FULL = 'full'
    UNKNOWN = 'statusUnknown'
    NORMAL_PARKING_CONDITIONS_SUSPENDED = 'normalParkingConditionsSuspended'
    SPECIAL_PARKING_CONDITIONS_IN_FORCE = 'specialParkingConditionsInForce'


@validataclass
class ParkingFacilityReference:
    id: str = StringValidator()


@validataclass
class ParkingFacilityStatus:
    parkingFacilityReference: ParkingFacilityReference = DataclassValidator(ParkingFacilityReference)
    parkingFacilityStatusTime: datetime = DateTimeValidator(
        local_timezone=ZoneInfo('Europe/Berlin'),
        target_timezone=timezone.utc,
    )
    parkingFacilityStatus: list[ParkingFacilityStatusType] = (
        ListValidator(EnumValidator(ParkingFacilityStatusType)),
        Default([]),
    )
    totalNumberOfVacantParkingSpaces: int | None = IntegerValidator(allow_strings=True), Default(None)
    totalParkingCapacityOverride: int | None = IntegerValidator(allow_strings=True), Default(None)
    totalParkingCapacityShortTermOverride: int | None = IntegerValidator(allow_strings=True), Default(None)
    totalParkingCapacityLongTermOverride: int | None = IntegerValidator(allow_strings=True), Default(None)

    def _get_realtime_capacity(self) -> int | None:
        if self.totalParkingCapacityOverride is not None:
            return self.totalParkingCapacityOverride
        # Without a total capacity, the short term and long term capacities add up to the total capacity
        if self.totalParkingCapacityShortTermOverride is None and self.totalParkingCapacityLongTermOverride is None:
            return None
        return (self.totalParkingCapacityShortTermOverride or 0) + (self.totalParkingCapacityLongTermOverride or 0)

    def _get_realtime_opening_status(self) -> OpeningStatus | None:
        if ParkingFacilityStatusType.OPEN in self.parkingFacilityStatus:
            return OpeningStatus.OPEN
        if ParkingFacilityStatusType.CLOSED in self.parkingFacilityStatus:
            return OpeningStatus.CLOSED
        if ParkingFacilityStatusType.UNKNOWN in self.parkingFacilityStatus:
            return OpeningStatus.UNKNOWN
        return None

    def to_realtime_parking_site_input(self) -> RealtimeParkingSiteInput:
        return RealtimeParkingSiteInput(
            uid=self.parkingFacilityReference.id,
            realtime_capacity=self._get_realtime_capacity(),
            realtime_free_capacity=self.totalNumberOfVacantParkingSpaces,
            realtime_data_updated_at=self.parkingFacilityStatusTime,
            realtime_opening_status=self._get_realtime_opening_status(),
        )
