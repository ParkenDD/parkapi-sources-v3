"""
Copyright 2023 binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

from datetime import datetime
from decimal import Decimal

from shapely.geometry.base import BaseGeometry
from validataclass.dataclasses import Default, DefaultUnset, validataclass
from validataclass.exceptions import DataclassPostValidationError, ValidationError
from validataclass.helpers import UnsetValueType
from validataclass.validators import (
    AnythingValidator,
    BooleanValidator,
    DataclassValidator,
    EnumValidator,
    IntegerValidator,
    ListValidator,
    Noneable,
    StringValidator,
    UrlValidator,
)

from .base_parking_inputs import RealtimeBaseParkingInput, StaticBaseParkingInput
from .enums import (
    OpeningStatus,
    ParkAndRideType,
    ParkingSiteOrientation,
    ParkingSiteSide,
    ParkingSiteType,
    ParkingType,
    PurposeType,
    SupervisionType,
)
from .shared_inputs import ExternalIdentifierInput, ParkingRestrictionInput


@validataclass
class ParkingSiteRestrictionInput(ParkingRestrictionInput):
    capacity: int | None = Noneable(IntegerValidator()), Default(None)
    realtime_capacity: int | None = Noneable(IntegerValidator()), Default(None)
    realtime_free_capacity: int | None = Noneable(IntegerValidator()), Default(None)


@validataclass
class StaticParkingSiteInput(StaticBaseParkingInput):
    name: str = StringValidator(min_length=1, max_length=256)
    group_uid: str | None = Noneable(StringValidator(min_length=1, max_length=256)), Default(None)
    operator_name: str | None = StringValidator(max_length=256), Default(None)
    public_url: str | None = Noneable(UrlValidator(max_length=4096)), Default(None)

    type: ParkingSiteType = EnumValidator(ParkingSiteType)

    max_stay: int | None = Noneable(IntegerValidator(min_value=0, allow_strings=True)), Default(None)
    max_height: int | None = Noneable(IntegerValidator(min_value=0, allow_strings=True)), Default(None)
    max_width: int | None = Noneable(IntegerValidator(min_value=0, allow_strings=True)), Default(None)
    has_lighting: bool | None = Noneable(BooleanValidator()), Default(None)
    is_covered: bool | None = Noneable(BooleanValidator()), Default(None)
    fee_description: str | None = Noneable(StringValidator(max_length=4096)), Default(None)
    has_fee: bool | None = Noneable(BooleanValidator()), Default(None)
    park_and_ride_type: list[ParkAndRideType] = (
        Noneable(ListValidator(EnumValidator(ParkAndRideType))),
        Default([]),
    )

    restrictions: list[ParkingSiteRestrictionInput] = (
        Noneable(ListValidator(DataclassValidator(ParkingSiteRestrictionInput))),
        Default([]),
    )

    orientation: ParkingSiteOrientation | None = Noneable(EnumValidator(ParkingSiteOrientation)), Default(None)
    side: ParkingSiteSide | None = Noneable(EnumValidator(ParkingSiteSide)), Default(None)
    parking_type: ParkingType | None = Noneable(EnumValidator(ParkingType)), Default(None)

    supervision_type: SupervisionType | None = Noneable(EnumValidator(SupervisionType)), Default(None)
    related_location: str | None = Noneable(StringValidator(max_length=256)), Default(None)

    capacity: int = IntegerValidator(min_value=0, allow_strings=True)
    capacity_min: int | None = Noneable(IntegerValidator(min_value=0, allow_strings=True)), Default(None)
    capacity_max: int | None = Noneable(IntegerValidator(min_value=0, allow_strings=True)), Default(None)

    opening_hours: str | None = Noneable(StringValidator(max_length=512)), Default(None)

    @property
    def is_supervised(self) -> bool | None:
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
class StaticPatchInput:
    items: list[dict] = ListValidator(AnythingValidator(allowed_types=[dict]))


@validataclass
class StaticParkingSitePatchInput(StaticParkingSiteInput):
    """
    This validataclass is for patching StaticParkingSiteInputs
    """

    name: str | UnsetValueType = DefaultUnset
    address: str | None | UnsetValueType = DefaultUnset
    purpose: PurposeType | UnsetValueType = DefaultUnset
    type: ParkingSiteType | UnsetValueType = DefaultUnset
    description: str | None | UnsetValueType = DefaultUnset

    lat: Decimal | UnsetValueType = DefaultUnset
    lon: Decimal | UnsetValueType = DefaultUnset

    capacity: int | UnsetValueType = DefaultUnset
    has_realtime_data: bool | UnsetValueType = DefaultUnset
    static_data_updated_at: datetime | UnsetValueType = DefaultUnset

    geojson: BaseGeometry | None | UnsetValueType = DefaultUnset
    tags: list[str] | UnsetValueType = DefaultUnset
    restrictions: list[ParkingSiteRestrictionInput] | UnsetValueType = DefaultUnset
    external_identifiers: list[ExternalIdentifierInput] | UnsetValueType = DefaultUnset

    group_uid: str | None | UnsetValueType = DefaultUnset
    operator_name: str | None | UnsetValueType = DefaultUnset
    public_url: str | None | UnsetValueType = DefaultUnset

    max_stay: int | None | UnsetValueType = DefaultUnset
    max_height: int | None | UnsetValueType = DefaultUnset
    max_width: int | None | UnsetValueType = DefaultUnset
    has_lighting: bool | None | UnsetValueType = DefaultUnset
    is_covered: bool | None | UnsetValueType = DefaultUnset
    fee_description: str | None | UnsetValueType = DefaultUnset
    has_fee: bool | None | UnsetValueType = DefaultUnset
    park_and_ride_type: list[ParkAndRideType] | UnsetValueType = DefaultUnset

    orientation: ParkingSiteOrientation | None | UnsetValueType = DefaultUnset
    side: ParkingSiteSide | None | UnsetValueType = DefaultUnset
    parking_type: ParkingType | None | UnsetValueType = DefaultUnset

    supervision_type: SupervisionType | None | UnsetValueType = DefaultUnset
    photo_url: str | None | UnsetValueType = DefaultUnset
    related_location: str | None | UnsetValueType = DefaultUnset

    capacity_min: int | None | UnsetValueType = DefaultUnset
    capacity_max: int | None | UnsetValueType = DefaultUnset

    opening_hours: str | None | UnsetValueType = DefaultUnset

    def __post_init__(self):
        # Don't do additional validation checks
        pass


@validataclass
class RealtimeParkingSiteInput(RealtimeBaseParkingInput):
    realtime_opening_status: OpeningStatus | None = Noneable(EnumValidator(OpeningStatus)), Default(None)
    realtime_capacity: int | None = Noneable(IntegerValidator(min_value=0, allow_strings=True)), Default(None)

    realtime_free_capacity: int | None = Noneable(IntegerValidator(min_value=0, allow_strings=True)), Default(None)

    restrictions: list[ParkingSiteRestrictionInput] = (
        Noneable(ListValidator(DataclassValidator(ParkingSiteRestrictionInput))),
        Default([]),
    )


@validataclass
class CombinedParkingSiteInput(StaticParkingSiteInput, RealtimeParkingSiteInput): ...
