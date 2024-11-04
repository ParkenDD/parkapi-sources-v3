"""
Copyright 2024 binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

from datetime import datetime
from enum import Enum

from validataclass.dataclasses import validataclass
from validataclass.exceptions import ValidationError
from validataclass.validators import EnumValidator, IntegerValidator, StringValidator

from parkapi_sources.models import RealtimeParkingSiteInput
from parkapi_sources.models.enums import OpeningStatus
from parkapi_sources.validators import TimestampDateTimeValidator


class BietigheimBissingenOpeningStatus(Enum):
    OPEN = 'Geöffnet'
    CLOSED = 'Geschlossen'

    def to_realtime_opening_status(self) -> OpeningStatus | None:
        return {
            self.OPEN: OpeningStatus.OPEN,
            self.CLOSED: OpeningStatus.CLOSED,
        }.get(self)


@validataclass
class BietigheimBissingenInput:
    Name: str = StringValidator()
    OpeningState: BietigheimBissingenOpeningStatus = EnumValidator(BietigheimBissingenOpeningStatus)
    Capacity: int = IntegerValidator(allow_strings=True)
    OccupiedSites: int = IntegerValidator(allow_strings=True)
    Timestamp: datetime = TimestampDateTimeValidator(allow_strings=True, divisor=1000)

    def __post_init__(self):
        if self.Capacity < self.OccupiedSites:
            raise ValidationError(reason='More occupied sites than capacity')

    def to_realtime_parking_site_input(self) -> RealtimeParkingSiteInput:
        return RealtimeParkingSiteInput(
            uid=self.Name,
            realtime_opening_status=self.OpeningState.to_realtime_opening_status(),
            realtime_capacity=self.Capacity,
            realtime_free_capacity=self.Capacity - self.OccupiedSites,
            realtime_data_updated_at=self.Timestamp,
        )
