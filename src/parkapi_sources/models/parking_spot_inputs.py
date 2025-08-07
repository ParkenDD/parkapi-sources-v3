"""
Copyright 2025 binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

from datetime import datetime, timezone
from decimal import Decimal

from shapely.geometry.base import BaseGeometry
from validataclass.dataclasses import Default, ValidataclassMixin, validataclass
from validataclass.validators import (
    BooleanValidator,
    DataclassValidator,
    DateTimeValidator,
    EnumValidator,
    ListValidator,
    Noneable,
    NumericValidator,
    StringValidator,
)

from parkapi_sources.validators import GeoJSONGeometryValidator

from .enums import ParkingSpotStatus, ParkingSpotType, PurposeType
from .parking_restriction_inputs import ParkingRestrictionInput
from .parking_site_inputs import ExternalIdentifierInput


@validataclass
class StaticParkingSpotInput(ValidataclassMixin):
    uid: str = StringValidator(min_length=1, max_length=256)
    name: str | None = Noneable(StringValidator(min_length=1, max_length=256)), Default(None)
    address: str | None = Noneable(StringValidator(max_length=256)), Default(None)
    purpose: PurposeType = EnumValidator(PurposeType), Default(PurposeType.CAR)
    type: ParkingSpotType | None = Noneable(EnumValidator(ParkingSpotType)), Default(None)
    description: str | None = Noneable(StringValidator(max_length=4096)), Default(None)
    static_data_updated_at: datetime = DateTimeValidator(
        local_timezone=timezone.utc,
        target_timezone=timezone.utc,
        discard_milliseconds=True,
    )

    has_realtime_data: bool = BooleanValidator()

    # Set min/max to Europe borders
    lat: Decimal = NumericValidator(min_value=34, max_value=72)
    lon: Decimal = NumericValidator(min_value=-27, max_value=43)

    geojson: BaseGeometry | None = Noneable(GeoJSONGeometryValidator()), Default(None)

    restricted_to: list[ParkingRestrictionInput] = (
        Noneable(ListValidator(DataclassValidator(ParkingRestrictionInput))),
        Default([]),
    )
    external_identifiers: list[ExternalIdentifierInput] = (
        Noneable(ListValidator(DataclassValidator(ExternalIdentifierInput))),
        Default([]),
    )
    tags: list[str] = ListValidator(StringValidator(min_length=1)), Default([])


@validataclass
class RealtimeParkingSpotInput(ValidataclassMixin):
    uid: str = StringValidator(min_length=1, max_length=256)
    realtime_data_updated_at: datetime = DateTimeValidator(
        local_timezone=timezone.utc,
        target_timezone=timezone.utc,
        discard_milliseconds=True,
    )
    realtime_status: ParkingSpotStatus | None = EnumValidator(ParkingSpotStatus), Default(None)


@validataclass
class CombinedParkingSpotInput(StaticParkingSpotInput, RealtimeParkingSpotInput): ...
