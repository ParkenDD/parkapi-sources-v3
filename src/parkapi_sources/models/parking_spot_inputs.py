"""
Copyright 2025 binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

from datetime import datetime, timezone
from decimal import Decimal

from validataclass.dataclasses import Default, ValidataclassMixin, validataclass
from validataclass.validators import (
    AnyOfValidator,
    BooleanValidator,
    DataclassValidator,
    DateTimeValidator,
    EnumValidator,
    FloatValidator,
    ListValidator,
    Noneable,
    NumericValidator,
    StringValidator,
)

from .enums import ParkingSpotStatus, ParkingSpotType, PurposeType
from .parking_restriction_inputs import ParkingRestrictionInput


@validataclass
class GeojsonPolygonInput(ValidataclassMixin):
    type: str = AnyOfValidator(allowed_values=['Polygon'])
    coordinates: list[list[list[float]]] = ListValidator(
        ListValidator(
            ListValidator(
                FloatValidator(allow_integers=True),
                min_length=2,
                max_length=2,
            ),
        ),
        min_length=1,
        max_length=1,
    )


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

    geojson: GeojsonPolygonInput | None = Noneable(DataclassValidator(GeojsonPolygonInput)), Default(None)

    restricted_to: list[ParkingRestrictionInput] | None = (
        Noneable(ListValidator(DataclassValidator(ParkingRestrictionInput))),
        Default(None),
    )


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
