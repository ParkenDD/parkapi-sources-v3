"""
Copyright 2023 binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

from datetime import datetime, timezone
from decimal import Decimal
from typing import Optional

from validataclass.dataclasses import Default, DefaultUnset, ValidataclassMixin, validataclass
from validataclass.exceptions import DataclassPostValidationError, ValidationError
from validataclass.helpers import OptionalUnsetNone
from validataclass.validators import (
    BooleanValidator,
    DataclassValidator,
    DateTimeValidator,
    EnumValidator,
    IntegerValidator,
    ListValidator,
    Noneable,
    NumericValidator,
    StringValidator,
    UrlValidator,
)

from .enums import ExternalIdentifierType, OpeningStatus, ParkAndRideType, ParkingSiteType, PurposeType, SupervisionType


@validataclass
class BaseParkingSiteInput(ValidataclassMixin):
    uid: str = StringValidator(min_length=1, max_length=256)


@validataclass
class ExternalIdentifierInput(ValidataclassMixin):
    type: ExternalIdentifierType = EnumValidator(ExternalIdentifierType)
    value: str = StringValidator(max_length=256)


@validataclass
class StaticParkingSiteInput(BaseParkingSiteInput):
    name: str = StringValidator(min_length=1, max_length=256)
    group_uid: OptionalUnsetNone[str] = Noneable(StringValidator(min_length=1, max_length=256)), DefaultUnset
    purpose: PurposeType = EnumValidator(PurposeType), Default(PurposeType.CAR)
    operator_name: OptionalUnsetNone[str] = StringValidator(max_length=256), DefaultUnset
    public_url: OptionalUnsetNone[str] = Noneable(UrlValidator(max_length=4096)), DefaultUnset
    address: OptionalUnsetNone[str] = Noneable(StringValidator(max_length=512)), DefaultUnset
    description: OptionalUnsetNone[str] = Noneable(StringValidator(max_length=4096)), DefaultUnset
    type: ParkingSiteType = EnumValidator(ParkingSiteType)

    max_stay: OptionalUnsetNone[int] = Noneable(IntegerValidator(min_value=0, allow_strings=True)), DefaultUnset
    max_height: OptionalUnsetNone[int] = Noneable(IntegerValidator(min_value=0, allow_strings=True)), DefaultUnset
    max_width: OptionalUnsetNone[int] = Noneable(IntegerValidator(min_value=0, allow_strings=True)), DefaultUnset
    has_lighting: OptionalUnsetNone[bool] = Noneable(BooleanValidator()), DefaultUnset
    is_covered: OptionalUnsetNone[bool] = Noneable(BooleanValidator()), DefaultUnset
    fee_description: OptionalUnsetNone[str] = Noneable(StringValidator(max_length=4096)), DefaultUnset
    has_fee: OptionalUnsetNone[bool] = Noneable(BooleanValidator()), DefaultUnset
    park_and_ride_type: OptionalUnsetNone[list[ParkAndRideType]] = (
        Noneable(
            ListValidator(EnumValidator(ParkAndRideType)),
        ),
        DefaultUnset,
    )
    supervision_type: OptionalUnsetNone[SupervisionType] = Noneable(EnumValidator(SupervisionType)), DefaultUnset
    photo_url: OptionalUnsetNone[str] = Noneable(UrlValidator(max_length=4096)), DefaultUnset
    related_location: OptionalUnsetNone[str] = Noneable(StringValidator(max_length=256)), DefaultUnset

    has_realtime_data: OptionalUnsetNone[bool] = Noneable(BooleanValidator(), default=False), DefaultUnset
    static_data_updated_at: OptionalUnsetNone[datetime] = (
        DateTimeValidator(
            local_timezone=timezone.utc,
            target_timezone=timezone.utc,
            discard_milliseconds=True,
        ),
        DefaultUnset,
    )

    # Set min/max to Europe borders
    lat: Decimal = NumericValidator(min_value=34, max_value=72)
    lon: Decimal = NumericValidator(min_value=-27, max_value=43)

    capacity: int = IntegerValidator(min_value=0, allow_strings=True)
    capacity_disabled: OptionalUnsetNone[int] = (
        Noneable(IntegerValidator(min_value=0, allow_strings=True)),
        DefaultUnset,
    )
    capacity_woman: OptionalUnsetNone[int] = Noneable(IntegerValidator(min_value=0, allow_strings=True)), DefaultUnset
    capacity_family: OptionalUnsetNone[int] = Noneable(IntegerValidator(min_value=0, allow_strings=True)), DefaultUnset
    capacity_charging: OptionalUnsetNone[int] = (
        Noneable(IntegerValidator(min_value=0, allow_strings=True)),
        DefaultUnset,
    )
    capacity_carsharing: OptionalUnsetNone[int] = (
        Noneable(IntegerValidator(min_value=0, allow_strings=True)),
        DefaultUnset,
    )
    capacity_truck: OptionalUnsetNone[int] = Noneable(IntegerValidator(min_value=0, allow_strings=True)), DefaultUnset
    capacity_bus: OptionalUnsetNone[int] = Noneable(IntegerValidator(min_value=0, allow_strings=True)), DefaultUnset

    opening_hours: OptionalUnsetNone[str] = Noneable(StringValidator(max_length=512)), DefaultUnset

    external_identifiers: OptionalUnsetNone[list[ExternalIdentifierInput]] = (
        Noneable(ListValidator(DataclassValidator(ExternalIdentifierInput))),
        DefaultUnset,
    )
    tags: list[str] = ListValidator(StringValidator(min_length=1)), Default([])

    @property
    def is_supervised(self) -> Optional[bool]:
        if self.supervision_type is None:
            return None
        return self.supervision_type in [SupervisionType.YES, SupervisionType.VIDEO, SupervisionType.ATTENDED]

    def __post_init__(self):
        if self.lat == 0 and self.lon == 0:
            raise DataclassPostValidationError(
                error=ValidationError(code='lat_lon_zero', reason='Latitude and longitude are both zero.'),
            )

        if self.park_and_ride_type:
            if (
                ParkAndRideType.NO in self.park_and_ride_type or ParkAndRideType.YES in self.park_and_ride_type
            ) and len(self.park_and_ride_type) > 1:
                raise DataclassPostValidationError(
                    error=ValidationError(
                        code='invalid_park_ride_combination',
                        reason='YES and NO cannot be used with specific ParkAndRideTypes',
                    ),
                )


@validataclass
class RealtimeParkingSiteInput(BaseParkingSiteInput):
    uid: str = StringValidator(min_length=1, max_length=256)
    realtime_data_updated_at: datetime = DateTimeValidator(
        local_timezone=timezone.utc,
        target_timezone=timezone.utc,
        discard_milliseconds=True,
    )
    realtime_opening_status: OptionalUnsetNone[OpeningStatus] = Noneable(EnumValidator(OpeningStatus)), Default(None)
    realtime_capacity: OptionalUnsetNone[int] = (
        Noneable(IntegerValidator(min_value=0, allow_strings=True)),
        DefaultUnset,
    )
    realtime_capacity_disabled: OptionalUnsetNone[int] = (
        Noneable(IntegerValidator(min_value=0, allow_strings=True)),
        DefaultUnset,
    )
    realtime_capacity_woman: OptionalUnsetNone[int] = (
        Noneable(IntegerValidator(min_value=0, allow_strings=True)),
        DefaultUnset,
    )
    realtime_capacity_family: OptionalUnsetNone[int] = (
        Noneable(IntegerValidator(min_value=0, allow_strings=True)),
        DefaultUnset,
    )
    realtime_capacity_charging: OptionalUnsetNone[int] = (
        Noneable(IntegerValidator(min_value=0, allow_strings=True)),
        DefaultUnset,
    )
    realtime_capacity_carsharing: OptionalUnsetNone[int] = (
        Noneable(IntegerValidator(min_value=0, allow_strings=True)),
        DefaultUnset,
    )
    realtime_capacity_truck: OptionalUnsetNone[int] = (
        Noneable(IntegerValidator(min_value=0, allow_strings=True)),
        DefaultUnset,
    )
    realtime_capacity_bus: OptionalUnsetNone[int] = (
        Noneable(IntegerValidator(min_value=0, allow_strings=True)),
        DefaultUnset,
    )

    realtime_free_capacity: OptionalUnsetNone[int] = (
        Noneable(IntegerValidator(min_value=0, allow_strings=True)),
        DefaultUnset,
    )
    realtime_free_capacity_disabled: OptionalUnsetNone[int] = (
        Noneable(IntegerValidator(min_value=0, allow_strings=True)),
        DefaultUnset,
    )
    realtime_free_capacity_woman: OptionalUnsetNone[int] = (
        Noneable(IntegerValidator(min_value=0, allow_strings=True)),
        DefaultUnset,
    )
    realtime_free_capacity_family: OptionalUnsetNone[int] = (
        Noneable(IntegerValidator(min_value=0, allow_strings=True)),
        DefaultUnset,
    )
    realtime_free_capacity_charging: OptionalUnsetNone[int] = (
        Noneable(IntegerValidator(min_value=0, allow_strings=True)),
        DefaultUnset,
    )
    realtime_free_capacity_carsharing: OptionalUnsetNone[int] = (
        Noneable(IntegerValidator(min_value=0, allow_strings=True)),
        DefaultUnset,
    )
    realtime_free_capacity_truck: OptionalUnsetNone[int] = (
        Noneable(IntegerValidator(min_value=0, allow_strings=True)),
        DefaultUnset,
    )
    realtime_free_capacity_bus: OptionalUnsetNone[int] = (
        Noneable(IntegerValidator(min_value=0, allow_strings=True)),
        DefaultUnset,
    )
