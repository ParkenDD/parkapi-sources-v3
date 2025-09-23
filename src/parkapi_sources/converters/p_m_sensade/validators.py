"""
Copyright 2025 binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

from datetime import datetime, timezone
from zoneinfo import ZoneInfo
from decimal import Decimal

from validataclass.dataclasses import Default, validataclass
from validataclass.validators import (
    BooleanValidator,
    DateTimeValidator,
    IntegerValidator,
    Noneable,
    StringValidator,
    ListValidator,
    AnythingValidator,
    NumericValidator,
    DataclassValidator,
)

from parkapi_sources.models import (
    RealtimeParkingSiteInput,
    StaticParkingSiteInput,
)
from parkapi_sources.models.enums import ParkingSiteType, ParkAndRideType


@validataclass
class PMSensadeParkingLotInput:
    id: str = StringValidator(min_length=1, max_length=256)
    name: str = StringValidator(min_length=1, max_length=256)
    latitude: Decimal = NumericValidator(min_value=34, max_value=72)
    longitude: Decimal = NumericValidator(min_value=-27, max_value=43)
    freeParking: bool | None = Noneable(BooleanValidator()), Default(None)
    ticketParking: bool | None = Noneable(BooleanValidator()), Default(None)
    hasLiveData: bool = BooleanValidator()
    city: str | None = Noneable(StringValidator(min_length=1, max_length=256)), Default(None)


@validataclass
class PMSensadeParkingLotParkingSpaces:
    id: str = StringValidator(min_length=1, max_length=256)
    type: str = StringValidator(min_length=1, max_length=256)
    number: str | None = Noneable(StringValidator(min_length=1, max_length=256)), Default(None)
    devEui: str | None = Noneable(StringValidator(min_length=1, max_length=256)), Default(None)
    latitude: Decimal = NumericValidator(min_value=34, max_value=72)
    longitude: Decimal = NumericValidator(min_value=-27, max_value=43)


@validataclass
class PMSensadeParkingLot:
    id: str = StringValidator(min_length=1, max_length=256)
    name: str = StringValidator(min_length=1, max_length=256)
    country: str | None = Noneable(StringValidator(min_length=1, max_length=256)), Default(None)
    city: str | None = Noneable(StringValidator(min_length=1, max_length=256)), Default(None)
    address: str | None = Noneable(StringValidator(min_length=1, max_length=256)), Default(None)
    zip: int | None = Noneable(IntegerValidator()), Default(None)
    availableSpaces: int = IntegerValidator(min_value=0, allow_strings=True)
    creationDate: datetime = DateTimeValidator(
        local_timezone=ZoneInfo('Europe/Berlin'),
        target_timezone=timezone.utc,
    )
    latitude: Decimal = NumericValidator(min_value=34, max_value=72)
    longitude: Decimal = NumericValidator(min_value=-27, max_value=43)
    parkingSpaces: list[dict] | None = Noneable(ListValidator(DataclassValidator(PMSensadeParkingLotParkingSpaces))), Default(None)

    def to_static_parking_site(self) -> StaticParkingSiteInput:
        if self.address and self.zip and self.city:
            address = f'{self.address}, {self.zip} {self.city}'
        elif self.address:
            address = f'{self.address}'
        else:
            address = None
        return StaticParkingSiteInput(
            uid=self.id,
            name=self.name,
            lat=self.latitude,
            lon=self.longitude,
            address=address,
            capacity=self.availableSpaces,
            static_data_updated_at=self.creationDate,
            type=ParkingSiteType.OFF_STREET_PARKING_GROUND,
            park_and_ride_type=[ParkAndRideType.YES],
            has_realtime_data=True,
        )
    

@validataclass
class PMSensadeParkingLotStatus:
    parkingLotId: str = StringValidator(min_length=1, max_length=256)
    parkingLotName: str = StringValidator(min_length=1, max_length=256)
    totalSpaceCount: int = IntegerValidator(min_value=0, allow_strings=True)
    availableSpaceCount: int = IntegerValidator(min_value=0, allow_strings=True)
    occupiedSpaceCount: int = IntegerValidator(min_value=0, allow_strings=True)

    def to_realtime_parking_site_input(self) -> RealtimeParkingSiteInput:
        return RealtimeParkingSiteInput(
            uid=self.id,
            realtime_capacity=self.totalSpaceCount,
            realtime_free_capacity=self.availableSpaceCount,
            realtime_data_updated_at=datetime.now(tz=timezone.utc),
        )
    
@validataclass
class PMSensadeParkingLotsInput:
    organizationId: str = StringValidator(min_length=1, max_length=256)
    organizationName: str = StringValidator(min_length=1, max_length=256)
    parkingLots: list[dict] = ListValidator(DataclassValidator(PMSensadeParkingLotInput))
