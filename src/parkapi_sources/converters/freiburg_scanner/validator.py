"""
Copyright 2025 binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

from datetime import datetime
from typing import Any

import shapely
from shapely import GeometryType, LineString
from validataclass.dataclasses import validataclass
from validataclass.exceptions import ValidationError
from validataclass.validators import (
    AnyOfValidator,
    DataclassValidator,
    IntegerValidator,
    StringValidator,
    Validator,
)

from parkapi_sources.models import StaticParkingSiteInput
from parkapi_sources.models.enums import ParkingSiteType
from parkapi_sources.util import round_7d
from parkapi_sources.validators import GeoJSONGeometryValidator


class FreiburgConfidenceIntervalFormatError(ValidationError):
    code = 'freiburg_confidence_format_error'


class FreiburgConfidenceIntervalValidator(Validator):
    def validate(self, input_data: Any, **kwargs: Any) -> tuple[int, int]:
        self._ensure_type(input_data, [str])

        if input_data[0] != '{' or input_data[-1] != '}':
            raise FreiburgConfidenceIntervalFormatError(reason='Confidence interval format is not correct')

        interval_items = input_data[1:-1].split(',')

        if len(interval_items) != 2:
            raise FreiburgConfidenceIntervalFormatError(reason='Confidence interval format is not correct')

        try:
            return int(interval_items[0]), int(interval_items[1])
        except ValueError as e:
            raise FreiburgConfidenceIntervalFormatError(reason='Confidence interval format is not correct') from e


@validataclass
class FreiburgScannerPropertiesInput:
    id: str = StringValidator()
    capacity: int = IntegerValidator()
    confidence_interval: tuple[int, int] = FreiburgConfidenceIntervalValidator()
    kr_strassenname: str = StringValidator()


@validataclass
class FreiburgScannerFeatureInput:
    type: str = AnyOfValidator(allowed_values=['Feature'])
    properties: FreiburgScannerPropertiesInput = DataclassValidator(FreiburgScannerPropertiesInput)
    geometry: LineString = GeoJSONGeometryValidator(allowed_geometry_types=[GeometryType.LINESTRING])

    def to_static_parking_site(self, static_data_updated_at: datetime) -> StaticParkingSiteInput | None:
        if self.properties.capacity == 0:
            return None

        center = shapely.centroid(self.geometry)

        return StaticParkingSiteInput(
            uid=str(self.properties.id),
            name=self.properties.kr_strassenname,
            address=f'{self.properties.kr_strassenname}, Freiburg',
            type=ParkingSiteType.ON_STREET,
            lat=round_7d(center.y),
            lon=round_7d(center.x),
            capacity=self.properties.capacity,
            capacity_min=self.properties.confidence_interval[0],
            capacity_max=self.properties.confidence_interval[1],
            geojson=self.geometry,
            static_data_updated_at=static_data_updated_at,
            has_realtime_data=False,
        )
