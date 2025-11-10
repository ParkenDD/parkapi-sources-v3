"""
Copyright 2025 binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

from abc import ABC
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
    UrlValidator,
)

from parkapi_sources.validators import GeoJSONGeometryValidator

from .enums import PurposeType
from .shared_inputs import ExternalIdentifierInput, ParkingRestrictionInput


@validataclass
class StaticBaseParkingInput(ValidataclassMixin, ABC):
    uid: str = StringValidator(min_length=1, max_length=256)

    purpose: PurposeType = EnumValidator(PurposeType), Default(PurposeType.CAR)
    address: str | None = Noneable(StringValidator(max_length=512)), Default(None)
    description: str | None = Noneable(StringValidator(max_length=4096)), Default(None)
    operator_name: str | None = Noneable(StringValidator(max_length=256)), Default(None)

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

    photo_url: str | None = Noneable(UrlValidator(max_length=4096)), Default(None)

    external_identifiers: list[ExternalIdentifierInput] = (
        Noneable(ListValidator(DataclassValidator(ExternalIdentifierInput))),
        Default([]),
    )
    tags: list[str] = ListValidator(StringValidator(min_length=1)), Default([])
    geojson: BaseGeometry | None = Noneable(GeoJSONGeometryValidator()), Default(None)

    restrictions: list[ParkingRestrictionInput] = (
        Noneable(ListValidator(DataclassValidator(ParkingRestrictionInput))),
        Default([]),
    )


@validataclass
class RealtimeBaseParkingInput(ValidataclassMixin, ABC):
    uid: str = StringValidator(min_length=1, max_length=256)

    realtime_data_updated_at: datetime = DateTimeValidator(
        local_timezone=timezone.utc,
        target_timezone=timezone.utc,
        discard_milliseconds=True,
    )
