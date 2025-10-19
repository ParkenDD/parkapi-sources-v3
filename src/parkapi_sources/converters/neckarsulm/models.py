"""
Copyright 2024 binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

from datetime import datetime, timezone
from decimal import Decimal
from enum import Enum
from typing import Optional

from validataclass.dataclasses import validataclass
from validataclass.validators import DecimalValidator, EnumValidator, IntegerValidator, StringValidator

from parkapi_sources.models import ParkingSiteRestrictionInput, StaticParkingSiteInput
from parkapi_sources.models.enums import ParkingAudience, ParkingSiteType
from parkapi_sources.validators import ExcelNoneable
from parkapi_sources.validators.boolean_validators import MappedBooleanValidator


class NeckarsulmParkingSiteType(Enum):
    OFF_STREET_PARKING_GROUND = 'Parkplatz'
    HIKING_OFF_STREET_PARKING_GROUND = 'Wanderparkplatz'
    CAR_PARK = 'Parkhaus'
    UNDERGROUND = 'Tiefgarage'
    # there is the value 'p+r', but as this is not a parking type, but an usecase, we just map this to off street parking ground
    PARK_AND_RIDE_OFF_STREET_PARKING_GROUND = 'p+r'

    def to_parking_site_type_input(self) -> ParkingSiteType:
        if self.name.endswith('OFF_STREET_PARKING_GROUND'):
            return ParkingSiteType.OFF_STREET_PARKING_GROUND

        return ParkingSiteType[self.name]


@validataclass
class NeckarsulmRowInput:
    uid: int = IntegerValidator(allow_strings=True)
    name: str = StringValidator(max_length=255)
    type: NeckarsulmParkingSiteType = EnumValidator(NeckarsulmParkingSiteType)
    lat: Decimal = DecimalValidator(min_value=40, max_value=60)
    lon: Decimal = DecimalValidator(min_value=7, max_value=10)
    street: Optional[str] = ExcelNoneable(StringValidator(max_length=255))
    postcode: Optional[str] = ExcelNoneable(StringValidator(max_length=255))
    city: Optional[str] = ExcelNoneable(StringValidator(max_length=255))
    # max_stay exists in the table as maxparken_1, but has no parsable data format
    capacity: int = IntegerValidator(allow_strings=True)
    capacity_carsharing: Optional[int] = ExcelNoneable(IntegerValidator(allow_strings=True))
    capacity_charging: Optional[int] = ExcelNoneable(IntegerValidator(allow_strings=True))
    capacity_woman: Optional[int] = ExcelNoneable(IntegerValidator(allow_strings=True))
    capacity_disabled: Optional[int] = ExcelNoneable(IntegerValidator(allow_strings=True))
    has_fee: Optional[bool] = ExcelNoneable(MappedBooleanValidator(mapping={'ja': True, 'nein': False}))
    opening_hours: Optional[str] = ExcelNoneable(StringValidator(max_length=255))
    max_height: Optional[Decimal] = ExcelNoneable(DecimalValidator())

    def to_static_parking_site_input(self) -> StaticParkingSiteInput:
        if self.street and self.postcode and self.city:
            address = f'{self.street}, {self.postcode} {self.city}'
        elif self.street:
            address = f'{self.street}, Neckarsulm'
        else:
            address = None

        restrictions: list[ParkingSiteRestrictionInput] = []
        if self.capacity_carsharing is not None:
            restrictions.append(
                ParkingSiteRestrictionInput(
                    type=ParkingAudience.CARSHARING,
                    capacity=self.capacity_carsharing,
                ),
            )
        if self.capacity_charging is not None:
            restrictions.append(
                ParkingSiteRestrictionInput(
                    type=ParkingAudience.CHARGING,
                    capacity=self.capacity_charging,
                ),
            )
        if self.capacity_woman is not None:
            restrictions.append(
                ParkingSiteRestrictionInput(
                    type=ParkingAudience.WOMEN,
                    capacity=self.capacity_woman,
                ),
            )
        if self.capacity_disabled is not None:
            restrictions.append(
                ParkingSiteRestrictionInput(
                    type=ParkingAudience.DISABLED,
                    capacity=self.capacity_disabled,
                ),
            )
        return StaticParkingSiteInput(
            uid=str(self.uid),
            name=self.name,
            type=self.type.to_parking_site_type_input(),
            lat=self.lat,
            lon=self.lon,
            address=address,
            capacity=self.capacity,
            restrictions=restrictions,
            has_fee=self.has_fee,
            opening_hours='24/7' if self.opening_hours == '00:00-24:00' else None,
            static_data_updated_at=datetime.now(tz=timezone.utc),
            max_height=int(self.max_height * 100) if self.max_height else None,
            has_realtime_data=False,
            # TODO: we could use the P+R type as park_and_ride_type, but for now p+r in data source is rather broken
        )
