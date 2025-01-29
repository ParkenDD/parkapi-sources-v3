"""
Copyright 2024 binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

from datetime import datetime, timezone
from decimal import Decimal
from enum import Enum
from zoneinfo import ZoneInfo

from validataclass.dataclasses import validataclass
from validataclass.validators import (
    DataclassValidator,
    EnumValidator,
    IntegerValidator,
    NumericValidator,
    StringValidator,
)

from parkapi_sources.models import RealtimeParkingSiteInput, StaticParkingSiteInput
from parkapi_sources.models.enums import ParkAndRideType, ParkingSiteType
from parkapi_sources.validators import SpacedDateTimeValidator


class PMBWConnectionStatus(Enum):
    OFFLINE = 'OFFLINE'
    ONLINE = 'ONLINE'
    ACTIVE = 'ACTIVE'


class PMBWCategory(Enum):
    P_M = 'P&M'


@validataclass
class PMBWCapacityInput:
    bus: int = IntegerValidator()
    car: int = IntegerValidator()
    car_charging: int = IntegerValidator()
    car_handicap: int = IntegerValidator()
    car_women: int = IntegerValidator()
    truck: int = IntegerValidator()


@validataclass
class PMBWLocationInput:
    lat: Decimal = NumericValidator()
    lng: Decimal = NumericValidator()


@validataclass
class PMBWInput:
    id: str = StringValidator()
    long_name: str = StringValidator()
    name: str = StringValidator()
    status: PMBWConnectionStatus = EnumValidator(PMBWConnectionStatus)
    time: datetime = SpacedDateTimeValidator(
        local_timezone=ZoneInfo('Europe/Berlin'),
        target_timezone=timezone.utc,
    )
    location: PMBWLocationInput = DataclassValidator(PMBWLocationInput)
    capacity: PMBWCapacityInput = DataclassValidator(PMBWCapacityInput)
    category: PMBWCategory = EnumValidator(PMBWCategory)
    free_capacity: PMBWCapacityInput = DataclassValidator(PMBWCapacityInput)

    def to_static_parking_site(self) -> StaticParkingSiteInput:
        return StaticParkingSiteInput(
            uid=self.id,
            name=self.long_name,
            static_data_updated_at=self.time,
            capacity=self.capacity.car,
            capacity_charging=self.capacity.car_charging,
            capacity_disabled=self.capacity.car_handicap,
            capacity_woman=self.capacity.car_women,
            has_realtime_data=True,
            lat=self.location.lat,
            lon=self.location.lng,
            type=ParkingSiteType.ON_STREET,
            park_and_ride_type=[ParkAndRideType.CARPOOL] if self.category == PMBWCategory.P_M else None,
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
