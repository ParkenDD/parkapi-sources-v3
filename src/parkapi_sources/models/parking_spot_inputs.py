"""
Copyright 2025 binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

from datetime import datetime, timezone
from decimal import Decimal

from shapely.geometry.base import BaseGeometry
from validataclass.dataclasses import Default, DefaultUnset, validataclass
from validataclass.exceptions import DataclassPostValidationError, RequiredValueError
from validataclass.helpers import UnsetValue, UnsetValueType
from validataclass.validators import (
    DataclassValidator,
    DateTimeValidator,
    EnumValidator,
    ListValidator,
    Noneable,
    StringValidator,
)

from .base_parking_inputs import RealtimeBaseParkingInput, StaticBaseParkingInput
from .enums import ParkingSpotStatus, ParkingSpotType, PurposeType
from .shared_inputs import ExternalIdentifierInput, ParkingRestrictionInput


@validataclass
class ParkingSpotRestrictionInput(ParkingRestrictionInput): ...


@validataclass
class StaticParkingSpotInput(StaticBaseParkingInput):
    name: str | None = Noneable(StringValidator(min_length=1, max_length=256)), Default(None)
    parking_site_uid: str | None = Noneable(StringValidator(min_length=1, max_length=256)), Default(None)

    type: ParkingSpotType | None = Noneable(EnumValidator(ParkingSpotType)), Default(None)

    restrictions: list[ParkingSpotRestrictionInput] = (
        Noneable(ListValidator(DataclassValidator(ParkingSpotRestrictionInput))),
        Default([]),
    )


@validataclass
class StaticParkingSpotPatchInput(StaticParkingSpotInput):
    name: str | None | UnsetValueType = DefaultUnset
    parking_site_uid: str | None | UnsetValueType = DefaultUnset
    address: str | None | UnsetValueType = DefaultUnset
    purpose: PurposeType | UnsetValueType = DefaultUnset
    type: ParkingSpotType | None | UnsetValueType = DefaultUnset
    description: str | None | UnsetValueType = DefaultUnset
    static_data_updated_at: datetime | UnsetValueType = DefaultUnset

    has_realtime_data: bool | UnsetValueType = DefaultUnset

    lat: Decimal | UnsetValueType = DefaultUnset
    lon: Decimal | UnsetValueType = DefaultUnset

    geojson: BaseGeometry | None | UnsetValueType = DefaultUnset

    restrictions: list[ParkingSpotRestrictionInput] | UnsetValueType = DefaultUnset
    external_identifiers: list[ExternalIdentifierInput] | UnsetValueType = DefaultUnset
    tags: list[str] | UnsetValueType = DefaultUnset


@validataclass
class RealtimeParkingSpotInput(RealtimeBaseParkingInput):
    realtime_status: ParkingSpotStatus | None = EnumValidator(ParkingSpotStatus), Default(None)


@validataclass
class CombinedParkingSpotInput(StaticParkingSpotInput, RealtimeParkingSpotInput):
    realtime_data_updated_at: datetime | UnsetValueType = (
        DateTimeValidator(
            local_timezone=timezone.utc,
            target_timezone=timezone.utc,
            discard_milliseconds=True,
        ),
        DefaultUnset,
    )

    def __post_init__(self):
        if self.has_realtime_data is True and self.realtime_data_updated_at is UnsetValue:
            raise DataclassPostValidationError(
                field_errors={
                    'realtime_data_updated_at': RequiredValueError(
                        reason='Realtime data updated at is required when has_realtime_data is set to True.',
                    ),
                },
            )
