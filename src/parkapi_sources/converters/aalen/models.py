"""
Copyright 2024 binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

from datetime import datetime, timezone
from enum import Enum

from validataclass.dataclasses import validataclass
from validataclass.validators import EnumValidator, IntegerValidator, StringValidator

from parkapi_sources.models import RealtimeParkingSiteInput
from parkapi_sources.models.enums import OpeningStatus


class AalenOpeningStatus(Enum):
    OPEN = 'geöffnet'
    CLOSED = 'geschlossen'
    OCCUPIED = 'besetzt'

    def to_realtime_opening_status(self) -> OpeningStatus | None:
        return {
            self.OPEN: OpeningStatus.OPEN,
            self.OCCUPIED: OpeningStatus.OPEN,
            self.CLOSED: OpeningStatus.CLOSED,
        }.get(self)


@validataclass
class AalenInput:
    name: str = StringValidator()
    status: AalenOpeningStatus = EnumValidator(AalenOpeningStatus)
    max: int = IntegerValidator()
    occupied: int = IntegerValidator()
    free: int = IntegerValidator()

    def to_realtime_parking_site_input(self) -> RealtimeParkingSiteInput:
        return RealtimeParkingSiteInput(
            uid=self.name,
            realtime_opening_status=self.status.to_realtime_opening_status(),
            realtime_capacity=self.max,
            realtime_free_capacity=self.free,
            realtime_data_updated_at=datetime.now(tz=timezone.utc),
        )
