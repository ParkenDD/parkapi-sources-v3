"""
Copyright 2025 binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

from datetime import datetime, timezone
from typing import Any

from shapely import GeometryType, Point
from validataclass.dataclasses import validataclass
from validataclass.exceptions import ValidationError
from validataclass.validators import DataclassValidator, IntegerValidator, StringValidator

from parkapi_sources.models import (
    GeojsonBaseFeatureInput,
    StaticParkingSpotInput,
)
from parkapi_sources.util import generate_point, round_7d
from parkapi_sources.validators import GeoJSONGeometryValidator


class InvalidKonstanzCountError(ValidationError):
    code = 'invalid_konstanz_count'


class KonstanzCountValidator(IntegerValidator):
    def validate(self, input_data: Any, **kwargs: Any) -> int:
        self._ensure_type(input_data, [str])

        input_data = input_data.split(' ')
        if len(input_data) != 2:
            raise InvalidKonstanzCountError()
        try:
            return int(input_data[0])
        except ValueError as e:
            raise InvalidKonstanzCountError() from e


@validataclass
class KonstanzDisabledPropertiesInput:
    OBJECTID: int = IntegerValidator()
    Name: str = StringValidator()
    Informatio: int = KonstanzCountValidator()
    GlobalID: str = StringValidator()


@validataclass
class KonstanzDisabledFeatureInput(GeojsonBaseFeatureInput):
    properties: KonstanzDisabledPropertiesInput = DataclassValidator(KonstanzDisabledPropertiesInput)
    geometry: Point = GeoJSONGeometryValidator(allowed_geometry_types=[GeometryType.POINT])

    def to_static_parking_spot_inputs(self) -> list[StaticParkingSpotInput]:
        static_parking_spot_inputs = []
        for i in range(self.properties.Informatio):
            lat, lon = generate_point(
                lat=round_7d(self.geometry.y),
                lon=round_7d(self.geometry.x),
                number=i,
                max_number=self.properties.Informatio,
            )

            static_parking_spot_inputs.append(
                StaticParkingSpotInput(
                    uid=f'{self.properties.GlobalID}_{i}',
                    name=f'{self.properties.Name} {i + 1} / {self.properties.Informatio}',
                    static_data_updated_at=datetime.now(tz=timezone.utc),
                    lat=lat,
                    lon=lon,
                    has_realtime_data=False,
                ),
            )

        return static_parking_spot_inputs
