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

    def to_static_parking_site(self, base_url: str) -> StaticParkingSiteInput:
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
            public_url=f'{base_url}/order/booking/?preselect_unit_uid={self.id[4:]}',
            opening_hours='24/7',
            has_fee=True,
        )

    def to_realtime_parking_site(self) -> RealtimeParkingSiteInput:
        return RealtimeParkingSiteInput(
            uid=self.id,
            realtime_data_updated_at=datetime.now(tz=timezone.utc),
            realtime_capacity=self.sum_boxes,
            realtime_free_capacity=self.bookable,
        )

    def extend_static_parking_site_input(self, static_parking_site_input: StaticParkingSiteInput):
        self.name = static_parking_site_input.name if static_parking_site_input.name else self.name
        self.purpose = static_parking_site_input.purpose if static_parking_site_input.purpose else self.purpose
        self.lat = static_parking_site_input.lat if static_parking_site_input.lat else self.lat
        self.long = static_parking_site_input.lon if static_parking_site_input.lon else self.long
        self.has_realtime_data = (
            static_parking_site_input.has_realtime_data
            if static_parking_site_input.has_realtime_data
            else self.has_realtime_data
        )
        self.capacity = static_parking_site_input.capacity if static_parking_site_input.capacity else self.capacity
        self.type = static_parking_site_input.type if static_parking_site_input.type else self.type
        self.static_data_updated_at = (
            static_parking_site_input.static_data_updated_at
            if static_parking_site_input.static_data_updated_at
            else self.static_data_updated_at
        )
        self.public_url = (
            static_parking_site_input.public_url if static_parking_site_input.public_url else self.public_url
        )
        self.opening_hours = (
            static_parking_site_input.opening_hours if static_parking_site_input.opening_hours else self.opening_hours
        )
        self.has_fee = static_parking_site_input.has_fee if static_parking_site_input.has_fee else self.has_fee
