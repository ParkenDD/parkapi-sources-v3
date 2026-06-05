"""
Copyright 2026 binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

from datetime import datetime, timezone
from decimal import Decimal
from enum import Enum

import shapely
from shapely import GeometryType, LineString
from validataclass.dataclasses import validataclass
from validataclass.validators import EnumValidator, IntegerValidator, StringValidator

from parkapi_sources.models import PurposeType, StaticParkingSiteInput
from parkapi_sources.models.enums import ParkingSiteOrientation, ParkingSiteType
from parkapi_sources.util import round_7d
from parkapi_sources.validators import ExcelNoneable, GermanDecimalValidator
from parkapi_sources.validators.csv_geojson_geometry_validator import CsvGeoJSONGeometryValidator


class ParkAngle(Enum):
    PARALLEL = 'parallel'
    PERPENDICULAR = 'perpendicular'
    DIAGONAL = 'diagonal'

    def to_parkind_site_orientation(self) -> ParkingSiteOrientation:
        if self == ParkingSiteOrientation.PARALLEL:
            return ParkingSiteOrientation.PARALLEL
        if self == ParkingSiteOrientation.PERPENDICULAR:
            return ParkingSiteOrientation.PERPENDICULAR
        if self == ParkingSiteOrientation.DIAGONAL:
            return ParkingSiteOrientation.DIAGONAL


class StreetSide(Enum):
    RIGHT = 'right'
    LEFT = 'left'


@validataclass
class FriedrichshafenEasyParkRowInput:
    id: int = IntegerValidator(allow_strings=True)
    length: Decimal = GermanDecimalValidator()
    park_angle: ParkAngle = EnumValidator(ParkAngle)
    street_side: StreetSide = EnumValidator(StreetSide)
    location_on_sidewalk: LineString = CsvGeoJSONGeometryValidator(allowed_geometry_types=[GeometryType.LINESTRING])
    permissions_translation: str = StringValidator()
    permission_period: str | None = ExcelNoneable(StringValidator())
    time_limited: str | None = ExcelNoneable(StringValidator())

    def to_static_parking_site_input(self) -> StaticParkingSiteInput:
        center = shapely.centroid(self.location_on_sidewalk)

        return StaticParkingSiteInput(
            uid=str(self.id),
            type=ParkingSiteType.ON_STREET,
            capacity=self._get_capacity(),
            orientation=self.park_angle.to_parkind_site_orientation(),
            name='Straßenparkplatz',
            purpose=PurposeType.CAR,
            side=self.street_side,
            description=self.permissions_translation,
            fee_description=self._get_fee_description(),
            has_realtime_data=False,
            static_data_updated_at=datetime.now(tz=timezone.utc),
            lon=round_7d(center.x),
            lat=round_7d(center.y),
            geojson=self.location_on_sidewalk,
            has_fee=True if self.permission_period and 'Gebührenpflichtig' in self.permission_period else False,
        )

    def _get_fee_description(self) -> str:
        fee_description = self.permissions_translation
        if self.permission_period:
            fee_description += self.permission_period
        if self.time_limited:
            fee_description += self.time_limited
        return fee_description

    def _get_capacity(self) -> int:
        if self.park_angle == ParkAngle.PARALLEL:
            return int(self.length / Decimal('5'))
        if self.park_angle == ParkAngle.PERPENDICULAR:
            return int(self.length / Decimal('2.5'))
        if self.park_angle == ParkAngle.DIAGONAL:
            return int(self.length / Decimal('3'))
