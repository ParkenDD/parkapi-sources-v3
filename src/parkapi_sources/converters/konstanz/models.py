"""
Copyright 2024 binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

from datetime import datetime
from decimal import Decimal
from enum import Enum
from typing import Optional

from validataclass.dataclasses import validataclass
from validataclass.validators import (
    AnythingValidator,
    DataclassValidator,
    EnumValidator,
    ListValidator,
    NumericValidator,
    StringValidator,
    UrlValidator,
)

from parkapi_sources.converters.konstanz.validators import (
    KonstanzHeightValidator,
    KonstanzOpeningTimeValidator,
    NumericIntegerValidator,
)
from parkapi_sources.models import RealtimeParkingSiteInput, StaticParkingSiteInput
from parkapi_sources.models.enums import OpeningStatus, ParkingSiteType
from parkapi_sources.validators import (
    EmptystringNoneable,
    GermanDurationIntegerValidator,
    MappedBooleanValidator,
    ReplacingStringValidator,
    TimestampDateTimeValidator,
)


class KonstanzOpeningStatus(Enum):
    CLOSED = '0'
    OPEN = '1'
    BROKEN = '2'

    def to_opening_status(self) -> OpeningStatus:
        return {
            self.OPEN: OpeningStatus.OPEN,
            self.CLOSED: OpeningStatus.CLOSED,
            self.BROKEN: OpeningStatus.CLOSED,
        }.get(self)


class KonstanzParkingSiteType(Enum):
    CAR_PARK = 'Parkhaus'
    UNDERGROUND = 'Tiefgarage'
    OFF_STREET_PARKING_GROUND = 'Parkplatz'

    def to_parking_site_type(self) -> ParkingSiteType:
        return {
            self.CAR_PARK: ParkingSiteType.CAR_PARK,
            self.UNDERGROUND: ParkingSiteType.UNDERGROUND,
            self.OFF_STREET_PARKING_GROUND: ParkingSiteType.OFF_STREET_PARKING_GROUND,
        }.get(self)


@validataclass
class KonstanzParkingSitesInput:
    features: list[dict] = ListValidator(AnythingValidator(allowed_types=[dict]))


@validataclass
class KonstanzParkingSiteDataInput:
    id: int = NumericIntegerValidator()
    name: str = StringValidator()
    max_cap: int = NumericIntegerValidator(min_value=0)
    type: KonstanzParkingSiteType = EnumValidator(KonstanzParkingSiteType)
    lat: Decimal = NumericValidator()
    lon: Decimal = NumericValidator()
    address: str = StringValidator()
    has_fee: bool = MappedBooleanValidator(mapping={'ja': True, 'nein': False})
    operator: str = StringValidator()
    max_stay: Optional[int] = EmptystringNoneable(GermanDurationIntegerValidator())
    opening_h: str = KonstanzOpeningTimeValidator()
    capacity_d: int = NumericIntegerValidator(min_value=0)
    capacity_c: int = NumericIntegerValidator(min_value=0)
    capacity_s: int = NumericIntegerValidator(min_value=0)
    capacity_w: int = NumericIntegerValidator(min_value=0)
    has_light: Optional[bool] = EmptystringNoneable(MappedBooleanValidator(mapping={'ja': True, 'nein': False}))
    descript: Optional[str] = EmptystringNoneable(StringValidator())
    public_url: Optional[str] = EmptystringNoneable(UrlValidator())
    fee_descr: Optional[str] = EmptystringNoneable(ReplacingStringValidator(mapping={'\n': ' ', '\r': ''}))
    park_ride: Optional[str] = EmptystringNoneable(StringValidator())
    has_live: bool = MappedBooleanValidator(mapping={'ja': True, 'nein': False})
    max_hei: int = EmptystringNoneable(KonstanzHeightValidator())
    opening_s: Optional[bool] = EmptystringNoneable(MappedBooleanValidator(mapping={'ja': True, 'nein': False}))
    updated: datetime = TimestampDateTimeValidator(divisor=1000)
    real_capa: int = NumericIntegerValidator(min_value=0)
    real_fcap: int = NumericIntegerValidator(min_value=0)

    def to_static_parking_site(self) -> StaticParkingSiteInput:
        return StaticParkingSiteInput(
            uid=str(self.id),
            name=self.name,
            operator_name=self.operator,
            public_url=self.public_url,
            address=self.address,
            description=self.descript,
            type=self.type.to_parking_site_type(),
            max_stay=self.max_stay,
            max_height=self.max_hei,
            has_lighting=self.has_light,
            fee_description=self.fee_descr,
            has_fee=self.has_fee,
            has_realtime_data=self.has_live,
            lat=self.lat,
            lon=self.lon,
            opening_hours=self.opening_h,
            capacity=self.max_cap,
            capacity_disabled=self.capacity_d,
            capacity_woman=self.capacity_w,
            static_data_updated_at=self.updated,
        )

    def to_realtime_parking_site(self) -> RealtimeParkingSiteInput:
        return RealtimeParkingSiteInput(
            uid=str(self.id),
            realtime_data_updated_at=self.updated,
            realtime_opening_status=OpeningStatus.OPEN if self.opening_s else OpeningStatus.CLOSED,
            realtime_capacity=self.real_capa,
            realtime_free_capacity=self.real_fcap,
        )


@validataclass
class KonstanzParkingSiteInput:
    attributes: KonstanzParkingSiteDataInput = DataclassValidator(KonstanzParkingSiteDataInput)

    def to_static_parking_site(self) -> StaticParkingSiteInput:
        return self.attributes.to_static_parking_site()

    def to_realtime_parking_site(self) -> RealtimeParkingSiteInput:
        return self.attributes.to_realtime_parking_site()
