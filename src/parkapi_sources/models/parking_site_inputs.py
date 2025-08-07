"""
Copyright 2023 binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

from datetime import datetime, timezone
from decimal import Decimal

from shapely.geometry.base import BaseGeometry
from validataclass.dataclasses import Default, DefaultUnset, ValidataclassMixin, validataclass
from validataclass.exceptions import DataclassPostValidationError, ValidationError
from validataclass.helpers import UnsetValueType
from validataclass.validators import (
    AnythingValidator,
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

from parkapi_sources.validators import GeoJSONGeometryValidator

from .enums import (
    ExternalIdentifierType,
    OpeningStatus,
    ParkAndRideType,
    ParkingSiteOrientation,
    ParkingSiteSide,
    ParkingSiteType,
    ParkingType,
    PurposeType,
    SupervisionType,
)
from .parking_restriction_inputs import ParkingRestrictionInput


@validataclass
class ExternalIdentifierInput(ValidataclassMixin):
    type: ExternalIdentifierType = EnumValidator(ExternalIdentifierType)
    value: str = StringValidator(max_length=256)


@validataclass
class StaticParkingSiteInput(ValidataclassMixin):
    uid: str = StringValidator(min_length=1, max_length=256)
    name: str = StringValidator(min_length=1, max_length=256)
    group_uid: str | None = Noneable(StringValidator(min_length=1, max_length=256)), Default(None)
    purpose: PurposeType = EnumValidator(PurposeType), Default(PurposeType.CAR)
    operator_name: str | None = StringValidator(max_length=256), Default(None)
    public_url: str | None = Noneable(UrlValidator(max_length=4096)), Default(None)
    address: str | None = Noneable(StringValidator(max_length=512)), Default(None)
    description: str | None = Noneable(StringValidator(max_length=4096)), Default(None)
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

    orientation: ParkingSiteOrientation | None = Noneable(EnumValidator(ParkingSiteOrientation)), Default(None)
    side: ParkingSiteSide | None = Noneable(EnumValidator(ParkingSiteSide)), Default(None)
    parking_type: ParkingType | None = Noneable(EnumValidator(ParkingType)), Default(None)

    supervision_type: SupervisionType | None = Noneable(EnumValidator(SupervisionType)), Default(None)
    photo_url: str | None = Noneable(UrlValidator(max_length=4096)), Default(None)
    related_location: str | None = Noneable(StringValidator(max_length=256)), Default(None)

    has_realtime_data: bool = BooleanValidator()
    static_data_updated_at: datetime = (
        DateTimeValidator(
            local_timezone=timezone.utc,
            target_timezone=timezone.utc,
            discard_milliseconds=True,
        ),
    )

    # Set min/max to Europe borders
    lat: Decimal = NumericValidator(min_value=34, max_value=72)
    lon: Decimal = NumericValidator(min_value=-27, max_value=43)

    capacity: int = IntegerValidator(min_value=0, allow_strings=True)
    capacity_min: int | None = Noneable(IntegerValidator(min_value=0, allow_strings=True)), Default(None)
    capacity_max: int | None = Noneable(IntegerValidator(min_value=0, allow_strings=True)), Default(None)
    capacity_disabled: int | None = (
        Noneable(IntegerValidator(min_value=0, allow_strings=True)),
        Default(None),
    )
    capacity_woman: int | None = Noneable(IntegerValidator(min_value=0, allow_strings=True)), Default(None)
    capacity_family: int | None = Noneable(IntegerValidator(min_value=0, allow_strings=True)), Default(None)
    capacity_charging: int | None = (
        Noneable(IntegerValidator(min_value=0, allow_strings=True)),
        Default(None),
    )
    capacity_carsharing: int | None = (
        Noneable(IntegerValidator(min_value=0, allow_strings=True)),
        Default(None),
    )
    capacity_truck: int | None = Noneable(IntegerValidator(min_value=0, allow_strings=True)), Default(None)
    capacity_bus: int | None = Noneable(IntegerValidator(min_value=0, allow_strings=True)), Default(None)

    opening_hours: str | None = Noneable(StringValidator(max_length=512)), Default(None)

    external_identifiers: list[ExternalIdentifierInput] = (
        Noneable(ListValidator(DataclassValidator(ExternalIdentifierInput))),
        Default([]),
    )
    tags: list[str] = ListValidator(StringValidator(min_length=1)), Default([])
    geojson: BaseGeometry | None = Noneable(GeoJSONGeometryValidator()), Default(None)

    restricted_to: list[ParkingRestrictionInput] = (
        Noneable(ListValidator(DataclassValidator(ParkingRestrictionInput))),
        Default([]),
    )

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

    uid: str = StringValidator(min_length=1, max_length=256)

    name: str | UnsetValueType = DefaultUnset
    purpose: PurposeType | UnsetValueType = DefaultUnset
    type: ParkingSiteType | UnsetValueType = DefaultUnset

    lat: Decimal | UnsetValueType = DefaultUnset
    lon: Decimal | UnsetValueType = DefaultUnset

    capacity: int | UnsetValueType = DefaultUnset
    has_realtime_data: bool | UnsetValueType = DefaultUnset
    static_data_updated_at: datetime | UnsetValueType = DefaultUnset

    tags: list[str] | UnsetValueType = DefaultUnset
    restricted_to: list[str] | UnsetValueType = DefaultUnset
    external_identifiers: list[dict] | UnsetValueType = DefaultUnset

    def __post_init__(self):
        # Don't do additional validation checks
        pass


@validataclass
class RealtimeParkingSiteInput(ValidataclassMixin):
    uid: str = StringValidator(min_length=1, max_length=256)
    realtime_data_updated_at: datetime = DateTimeValidator(
        local_timezone=timezone.utc,
        target_timezone=timezone.utc,
        discard_milliseconds=True,
    )
    realtime_opening_status: OpeningStatus | None = Noneable(EnumValidator(OpeningStatus)), Default(None)
    realtime_capacity: int | None = Noneable(IntegerValidator(min_value=0, allow_strings=True)), Default(None)
    realtime_capacity_disabled: int | None = Noneable(IntegerValidator(min_value=0, allow_strings=True)), Default(None)
    realtime_capacity_woman: int | None = Noneable(IntegerValidator(min_value=0, allow_strings=True)), Default(None)
    realtime_capacity_family: int | None = Noneable(IntegerValidator(min_value=0, allow_strings=True)), Default(None)
    realtime_capacity_charging: int | None = Noneable(IntegerValidator(min_value=0, allow_strings=True)), Default(None)
    realtime_capacity_carsharing: int | None = (
        Noneable(IntegerValidator(min_value=0, allow_strings=True)),
        Default(None),
    )
    realtime_capacity_truck: int | None = Noneable(IntegerValidator(min_value=0, allow_strings=True)), Default(None)
    realtime_capacity_bus: int | None = Noneable(IntegerValidator(min_value=0, allow_strings=True)), Default(None)

    realtime_free_capacity: int | None = Noneable(IntegerValidator(min_value=0, allow_strings=True)), Default(None)
    realtime_free_capacity_disabled: int | None = (
        Noneable(IntegerValidator(min_value=0, allow_strings=True)),
        Default(None),
    )
    realtime_free_capacity_woman: int | None = (
        Noneable(IntegerValidator(min_value=0, allow_strings=True)),
        Default(None),
    )
    realtime_free_capacity_family: int | None = (
        Noneable(IntegerValidator(min_value=0, allow_strings=True)),
        Default(None),
    )
    realtime_free_capacity_charging: int | None = (
        Noneable(IntegerValidator(min_value=0, allow_strings=True)),
        Default(None),
    )
    realtime_free_capacity_carsharing: int | None = (
        Noneable(IntegerValidator(min_value=0, allow_strings=True)),
        Default(None),
    )
    realtime_free_capacity_truck: int | None = (
        Noneable(IntegerValidator(min_value=0, allow_strings=True)),
        Default(None),
    )
    realtime_free_capacity_bus: int | None = (
        Noneable(IntegerValidator(min_value=0, allow_strings=True)),
        Default(None),
    )


@validataclass
class CombinedParkingSiteInput(StaticParkingSiteInput, RealtimeParkingSiteInput): ...
