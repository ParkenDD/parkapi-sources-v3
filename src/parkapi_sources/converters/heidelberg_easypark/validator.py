"""
Copyright 2025 binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

from datetime import datetime
from enum import Enum
from typing import Any

import pyproj
import shapely
from shapely import GeometryType, LineString
from validataclass.dataclasses import validataclass
from validataclass.validators import (
    AnyOfValidator,
    DataclassValidator,
    EnumValidator,
    IntegerValidator,
    StringValidator,
)

from parkapi_sources.models import StaticParkingSiteInput
from parkapi_sources.models.enums import ParkingSiteOrientation, ParkingSiteSide, ParkingSiteType
from parkapi_sources.util import round_7d
from parkapi_sources.validators import (
    EmptystringNoneable,
    FloatToIntegerValidators,
    GeoJSONGeometryValidator,
    SpacedDateTimeValidator,
)


class HeidelbergEasyparkOrientation(Enum):
    PARALLEL = 'Parallel'
    PERPENDICULAR = 'Senkrecht'
    DIAGONAL = 'Diagonal'
    FORBIDDEN = 'Parkverbot'

    def to_parking_side_orientation(self) -> ParkingSiteOrientation | None:
        return {
            self.PARALLEL: ParkingSiteOrientation.PARALLEL,
            self.DIAGONAL: ParkingSiteOrientation.DIAGONAL,
            self.PERPENDICULAR: ParkingSiteOrientation.PERPENDICULAR,
        }.get(self)


class HeidelbergEasyparkSide(Enum):
    RIGHT = 'rechts'
    LEFT = 'links'

    def to_parking_site_side(self) -> ParkingSiteSide:
        return {
            self.RIGHT: ParkingSiteSide.RIGHT,
            self.LEFT: ParkingSiteSide.LEFT,
        }.get(self)


@validataclass
class HeidelbergEasyParkPropertiesInput:
    Segment: int = IntegerValidator(allow_strings=True)
    Abstand1: str = StringValidator()
    Abstand2: str = StringValidator()
    Parkwinkel: HeidelbergEasyparkOrientation = EnumValidator(HeidelbergEasyparkOrientation)
    Strassense: HeidelbergEasyparkSide = EnumValidator(HeidelbergEasyparkSide)
    Bewirtscha: str | None = EmptystringNoneable(StringValidator())
    Erlaubnis: str = StringValidator()
    Erlaubnisz: str = StringValidator()
    Zeitlimit: str = StringValidator()
    Zeitlimitz: str = StringValidator()
    Ausrichtun: HeidelbergEasyparkOrientation = EnumValidator(HeidelbergEasyparkOrientation)
    Kapazitaet: int = FloatToIntegerValidators(allow_strings=True)
    Datenerfas: datetime = SpacedDateTimeValidator()
    Strassenna: str = StringValidator()
    Stadtteile: str = StringValidator()
    Lage: str = StringValidator()

    # TODO: Find a way to parse Erlaubnis together with times
    """
    Erlaubnis: list[HeidelbergEasyparkAllowTag] | None = EmptystringNoneable(
        CommaSeparatedListValidator(
            EnumValidator(HeidelbergEasyparkAllowTag),
        ),
    )
    """

    @staticmethod
    def __pre_validate__(input_data: Any, **kwargs: Any):
        key_mapping: dict[str, str] = {'Straßense': 'Strassense', 'Straßenna': 'Strassenna', 'Kapazität': 'Kapazitaet'}

        return {key_mapping.get(key, key): value for key, value in input_data.items()}


@validataclass
class HeidelbergEasyParkParkingSiteInput:
    type: str = AnyOfValidator(allowed_values=['Feature'])
    properties: HeidelbergEasyParkPropertiesInput = DataclassValidator(HeidelbergEasyParkPropertiesInput)
    geometry: LineString = GeoJSONGeometryValidator(
        allowed_geometry_types=[GeometryType.LINESTRING],
        projection=pyproj.Proj(proj='utm', zone=32, ellps='WGS84', preserve_units=True),
    )

    def to_static_parking_site(self, static_data_updated_at: datetime) -> StaticParkingSiteInput | None:
        if self.properties.Ausrichtun == HeidelbergEasyparkOrientation.FORBIDDEN:
            return None

        center = shapely.centroid(self.geometry)

        address = 'Heidelberg'
        if self.properties.Strassenna:
            address = f'{self.properties.Strassenna}, {address}'

        descriptions: list[str] = [
            self.properties.Erlaubnis,
            self.properties.Erlaubnisz,
            self.properties.Zeitlimit,
            self.properties.Zeitlimitz,
        ]

        return StaticParkingSiteInput(
            uid=f'{self.properties.Segment}-{self.properties.Abstand1}-{self.properties.Abstand2}',
            name=self.properties.Strassenna or 'Parkplatz',
            address=address,
            static_data_updated_at=static_data_updated_at,
            type=ParkingSiteType.ON_STREET,
            lat=round_7d(center.y),
            lon=round_7d(center.x),
            capacity=self.properties.Kapazitaet,
            description=' - '.join(description for description in descriptions if description != ''),
            has_fee=self.properties.Bewirtscha is not None,
            fee_description=self.properties.Bewirtscha or None,
            orientation=self.properties.Ausrichtun.to_parking_side_orientation(),
            side=self.properties.Strassense.to_parking_site_side(),
            geojson=self.geometry,
            has_realtime_data=False,
        )
