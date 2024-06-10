"""
Copyright 2024 binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

from datetime import datetime, timezone
from decimal import Decimal
from enum import Enum
from zoneinfo import ZoneInfo

from validataclass.dataclasses import validataclass
from validataclass.validators import DataclassValidator, EnumValidator, IntegerValidator, NumericValidator, StringValidator

from parkapi_sources.models import RealtimeParkingSiteInput, StaticParkingSiteInput
from parkapi_sources.models.enums import ParkAndRideType
from parkapi_sources.validators import SpacedDateTimeValidator


class A81PMConnectionStatus(Enum):
    OFFLINE = 'OFFLINE'
    ONLINE = 'ONLINE'


class A81PMCategory(Enum):
    P_M = 'P&M'


@validataclass
class A81PMCapacityInput:
    bus: int = IntegerValidator()
    car: int = IntegerValidator()
    car_charging: int = IntegerValidator()
    car_handicap: int = IntegerValidator()
    car_women: int = IntegerValidator()
    truck: int = IntegerValidator()


@validataclass
class A81PMLocationInput:
    lat: Decimal = NumericValidator()
    lng: Decimal = NumericValidator()


@validataclass
class A81PMInput:
    id: str = StringValidator()
    long_name: str = StringValidator()
    name: str = StringValidator()
    status: A81PMConnectionStatus = EnumValidator(A81PMConnectionStatus)  # TODO: what's that?
    time: datetime = SpacedDateTimeValidator(
        local_timezone=ZoneInfo('Europe/Berlin'),
        target_timezone=timezone.utc,
    )
    location: A81PMLocationInput = DataclassValidator(A81PMLocationInput)
    capacity: A81PMCapacityInput = DataclassValidator(A81PMCapacityInput)
    category: A81PMCategory = EnumValidator(A81PMCategory)
    free_capacity: A81PMCapacityInput = DataclassValidator(A81PMCapacityInput)

    def to_static_parking_site(self) -> StaticParkingSiteInput:
        return StaticParkingSiteInput(
            uid=self.id,
            name=self.long_name,
            static_data_updated_at=self.time,
            capacity=self.capacity.car,
            capacity_charging=self.capacity.car_charging,
            capacity_disabled=self.capacity.car_handicap,
            capacity_woman=self.capacity.car_women,
            lat=self.location.lat,
            lon=self.location.lng,
            park_and_ride_type=[ParkAndRideType.YES] if self.category == A81PMCategory.P_M else None,
        )

    def to_realtime_parking_site(self) -> RealtimeParkingSiteInput:
        return RealtimeParkingSiteInput(
            uid=self.id,
            realtime_capacity=self.capacity.car,
            realtime_capacity_charging=self.capacity.car_charging,
            realtime_capacity_disabled=self.capacity.car_handicap,
            realtime_capacity_woman=self.capacity.car_women,
            realtime_free_capacity=self.free_capacity.car,
            realtime_free_capacity_charging=self.free_capacity.car_charging,
            realtime_free_capacity_disabled=self.free_capacity.car_handicap,
            realtime_free_capacity_woman=self.free_capacity.car_women,
            realtime_data_updated_at=self.time,
        )
