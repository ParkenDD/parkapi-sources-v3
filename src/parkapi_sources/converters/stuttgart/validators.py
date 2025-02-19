"""
Copyright 2025 binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

from datetime import datetime, timezone
from decimal import Decimal
from enum import Enum
from zoneinfo import ZoneInfo

from validataclass.dataclasses import Default, validataclass
from validataclass.validators import (
    DataclassValidator,
    DateTimeValidator,
    DecimalValidator,
    EnumValidator,
    IntegerValidator,
    ListValidator,
    StringValidator,
)

from parkapi_sources.converters.base_converter.datex2 import ParkingFacility
from parkapi_sources.models import RealtimeParkingSiteInput
from parkapi_sources.models.enums import OpeningStatus


class ParkingFacilityStatusType(Enum):
    SPACES_AVAILABLE = 'spacesAvailable'
    OPEN = 'open'
    CLOSED = 'closed'
    FULL = 'full'
    UNKNOWN = 'statusUnknown'


@validataclass
class StuttgartLocationForDisplay:
    latitude: Decimal = DecimalValidator(min_value=5000000, max_value=6000000)
    longitude: Decimal = DecimalValidator(min_value=500000, max_value=600000)


@validataclass
class StuttgartFacilityLocation:
    locationForDisplay: StuttgartLocationForDisplay = DataclassValidator(StuttgartLocationForDisplay)


@validataclass
class StuttgartParkingFacility(ParkingFacility):
    facilityLocation: StuttgartFacilityLocation = DataclassValidator(StuttgartFacilityLocation)


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
    parkingFacilityStatus: list[ParkingFacilityStatusType] = ListValidator(EnumValidator(ParkingFacilityStatusType))
    totalNumberOfVacantParkingSpaces: int | None = IntegerValidator(allow_strings=True), Default(None)

    def to_realtime_parking_site_input(self) -> RealtimeParkingSiteInput:
        realtime_opening_status: OpeningStatus | None = None
        if ParkingFacilityStatusType.OPEN in self.parkingFacilityStatus:
            realtime_opening_status = OpeningStatus.OPEN
        elif ParkingFacilityStatusType.CLOSED in self.parkingFacilityStatus:
            realtime_opening_status = OpeningStatus.CLOSED
        elif ParkingFacilityStatusType.UNKNOWN in self.parkingFacilityStatus:
            realtime_opening_status = OpeningStatus.UNKNOWN

        return RealtimeParkingSiteInput(
            uid=self.parkingFacilityReference.id,
            realtime_free_capacity=self.totalNumberOfVacantParkingSpaces,
            realtime_data_updated_at=self.parkingFacilityStatusTime,
            realtime_opening_status=realtime_opening_status,
        )
