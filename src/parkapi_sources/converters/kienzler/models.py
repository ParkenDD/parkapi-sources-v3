"""
Copyright 2024 binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

from datetime import datetime, timezone
from decimal import Decimal

from validataclass.dataclasses import validataclass
from validataclass.validators import IntegerValidator, NumericValidator, StringValidator

from parkapi_sources.models import RealtimeParkingSiteInput, StaticParkingSiteInput
from parkapi_sources.models.enums import ParkingSiteType, PurposeType


@validataclass
class KienzlerInput:
    id: str = StringValidator(min_length=1)
    name: str = StringValidator()
    lat: Decimal = NumericValidator()
    long: Decimal = NumericValidator()
    bookable: int = IntegerValidator(min_value=0)
    sum_boxes: int = IntegerValidator(min_value=0)

    def to_static_parking_site(self) -> StaticParkingSiteInput:
        return StaticParkingSiteInput(
            uid=self.id,
            name=self.name,
            purpose=PurposeType.ITEM if 'Schließfächer' in self.name else PurposeType.BIKE,
            lat=self.lat,
            lon=self.long,
            has_realtime_data=True,
            capacity=self.sum_boxes,
            type=ParkingSiteType.LOCKERS,
            static_data_updated_at=datetime.now(tz=timezone.utc),
        )

    def to_realtime_parking_site(self) -> RealtimeParkingSiteInput:
        return RealtimeParkingSiteInput(
            uid=self.id,
            realtime_data_updated_at=datetime.now(tz=timezone.utc),
            realtime_capacity=self.sum_boxes,
            realtime_free_capacity=self.bookable,
        )
