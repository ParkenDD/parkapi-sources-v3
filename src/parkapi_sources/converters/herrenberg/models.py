"""
Copyright 2024 binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

from datetime import datetime, timezone
from decimal import Decimal
from enum import Enum
from typing import Optional

from validataclass.dataclasses import Default, validataclass
from validataclass.validators import (
    AnythingValidator,
    DataclassValidator,
    DateTimeValidator,
    EnumValidator,
    IntegerValidator,
    ListValidator,
    NumericValidator,
    StringValidator,
    UrlValidator,
)

from parkapi_sources.models import RealtimeParkingSiteInput, StaticParkingSiteInput
from parkapi_sources.models.enums import OpeningStatus, ParkAndRideType, ParkingSiteType


@validataclass
class HerrenbergParkingSitesInput:
    lots: list[dict] = ListValidator(AnythingValidator(allowed_types=[dict]))
    last_updated: datetime = DateTimeValidator(local_timezone=timezone.utc, target_timezone=timezone.utc)


class HerrenbergParkingSiteType(Enum):
    OFF_STREET_PARKING_GROUND = 'Parkplatz'
    CAR_PARK = 'Parkhaus'
    CARAVAN_PARKING = 'Wohnmobilparkplatz'
    CARPOOL = 'Park-Carpool'
    PARK_AND_RIDE = 'Park-Ride'
    ACCESSIBLE_PARKING = 'Barrierefreier-Parkplatz'
    UNDERGROUND_CAR_PARK = 'Tiefgarage'

    def to_parking_site_type(self) -> ParkingSiteType:
        return {
            self.OFF_STREET_PARKING_GROUND: ParkingSiteType.OFF_STREET_PARKING_GROUND,
            self.CAR_PARK: ParkingSiteType.CAR_PARK,
            self.CARAVAN_PARKING: ParkingSiteType.OFF_STREET_PARKING_GROUND,
            self.CARPOOL: ParkingSiteType.OFF_STREET_PARKING_GROUND,
            self.ACCESSIBLE_PARKING: ParkingSiteType.ON_STREET,
            self.UNDERGROUND_CAR_PARK: ParkingSiteType.CAR_PARK,
            self.PARK_AND_RIDE: ParkingSiteType.OFF_STREET_PARKING_GROUND,
        }.get(self)

    def to_park_and_ride_type(self) -> Optional[ParkingSiteType]:
        return {
            self.PARK_AND_RIDE: ParkAndRideType.YES,
            self.CARPOOL: ParkAndRideType.CARPOOL,
        }.get(self)


class HerrenbergState(Enum):
    NODATA = 'nodata'
    MANY = 'many'
    FULL = 'full'
    OPEN = 'open'
    CLOSED = 'closed'
    UNKNOWN = 'unknown'

    def to_opening_status(self) -> OpeningStatus | None:
        return {
            self.OPEN: OpeningStatus.OPEN,
            self.CLOSED: OpeningStatus.CLOSED,
            self.MANY: OpeningStatus.OPEN,
            self.FULL: OpeningStatus.OPEN,
        }.get(self)


@validataclass
class HerrenbergNotesInput:
    de: Optional[str] = StringValidator(max_length=512), Default(None)
    en: Optional[str] = StringValidator(max_length=512), Default(None)


@validataclass
class HerrenbergCoordsInput:
    lat: Decimal = NumericValidator()
    lng: Decimal = NumericValidator()


@validataclass
class HerrenbergParkingSiteInput:
    id: str = StringValidator(min_length=1, max_length=256)
    name: str = StringValidator(min_length=1, max_length=256)
    lot_type: HerrenbergParkingSiteType = EnumValidator(HerrenbergParkingSiteType)
    total: int = IntegerValidator(min_value=0)
    total_disabled: Optional[int] = IntegerValidator(min_value=0), Default(None)
    url: Optional[str] = UrlValidator(max_length=4096), Default(None)
    fee_hours: Optional[str] = StringValidator(max_length=4096), Default(None)
    opening_hours: Optional[str] = StringValidator(max_length=512), Default(None)
    address: str = StringValidator(max_length=512)
    notes: Optional[HerrenbergNotesInput] = DataclassValidator(HerrenbergNotesInput), Default(None)
    coords: HerrenbergCoordsInput = DataclassValidator(HerrenbergCoordsInput)
    state: Optional[HerrenbergState] = EnumValidator(HerrenbergState)
    free: Optional[int] = IntegerValidator(min_value=0), Default(None)

    def to_static_parking_site(self, static_data_updated_at: datetime) -> StaticParkingSiteInput:
        return StaticParkingSiteInput(
            uid=self.id,
            name=self.name,
            lat=self.coords.lat,
            lon=self.coords.lng,
            operator_name='Stadt Herrenberg',
            address=self.address,
            capacity=self.total,
            description=self.notes.de,
            type=self.lot_type.to_parking_site_type(),
            park_and_ride_type=[self.lot_type.to_park_and_ride_type()]
            if self.lot_type.to_park_and_ride_type()
            else None,
            public_url=self.url,
            opening_hours=self.opening_hours,
            has_fee=self.fee_hours is not None,
            capacity_disabled=self.total_disabled,
            has_realtime_data=self.state != HerrenbergState.NODATA,
            static_data_updated_at=static_data_updated_at,
        )

    def to_realtime_parking_site(self, realtime_data_updated_at: datetime) -> RealtimeParkingSiteInput:
        return RealtimeParkingSiteInput(
            uid=self.id,
            realtime_free_capacity=self.free,
            realtime_opening_status=self.state.to_opening_status(),
            realtime_data_updated_at=realtime_data_updated_at,
        )
