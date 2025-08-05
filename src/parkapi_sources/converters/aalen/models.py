"""
Copyright 2024 binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

from datetime import datetime, timezone
from enum import Enum

from validataclass.dataclasses import validataclass
from validataclass.validators import EnumValidator, IntegerValidator, StringValidator

from parkapi_sources.models import RealtimeParkingSiteInput, StaticParkingSiteInput
from parkapi_sources.models.enums import OpeningStatus


class AalenOpeningStatus(Enum):
    OPEN = 'geöffnet'
    CLOSED = 'geschlossen'
    OCCUPIED = 'besetzt'

    def to_realtime_opening_status(self) -> OpeningStatus | None:
        return {
            self.OPEN: OpeningStatus.OPEN,
            self.CLOSED: OpeningStatus.CLOSED,
            self.OCCUPIED: OpeningStatus.OPEN,
        }.get(self)


@validataclass
class AalenInput:
    name: str = StringValidator()
    status: AalenOpeningStatus = EnumValidator(AalenOpeningStatus)
    max: int = IntegerValidator(allow_strings=True)
    occupied: int = IntegerValidator(allow_strings=True)
    free: int = IntegerValidator(allow_strings=True)

    def to_realtime_parking_site_input(
        self, static_parking_site_input: StaticParkingSiteInput
    ) -> RealtimeParkingSiteInput:
        uid = static_parking_site_input.uid
        realtime_capacity = (
            self.max if self.max > static_parking_site_input.capacity else static_parking_site_input.capacity
        )
        return RealtimeParkingSiteInput(
            uid=uid,
            realtime_opening_status=self.status.to_realtime_opening_status(),
            realtime_capacity=realtime_capacity,
            realtime_free_capacity=self.free,
            realtime_data_updated_at=datetime.now(tz=timezone.utc),
        )
