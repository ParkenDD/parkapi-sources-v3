"""
Copyright 2026 binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

import re
from typing import Any, override

from shapely import GeometryType
from shapely.geometry.base import BaseGeometry
from validataclass.exceptions import ValidationError

from parkapi_sources.validators import GeoJSONGeometryValidator


class CsvGeoJSONGeometryValidator(GeoJSONGeometryValidator):
    def __init__(
        self,
        allowed_geometry_types: list[GeometryType] | None = None,
        **kwargs,
    ):
        if allowed_geometry_types != [GeometryType.LINESTRING]:
            # This exception is raised because the validator was not tested with other GeoJSONGeometry types.
            raise ValidationError(
                code='unsupported_geometry_type', reason='CsvGeoJSONGeometryValidator only supports LINESTRING'
            )
        super().__init__(allowed_geometry_types, **kwargs)

    @override
    def validate(self, input_data: Any, **kwargs: Any) -> BaseGeometry:
        if type(input_data) is not str:
            raise ValidationError(
                code='invalid_input_data_type', reason='Wrong datatype found for CsvGeoJSONGeometryValidator'
            )

        # This finds pairs of decimal numbers separated by a whitespace
        pattern = r'\d+.\d+\s\d+.\d+'
        points = re.findall(pattern, input_data)
        points_geojson_format = []
        for point in points:
            coordinate = point.split(' ')
            points_geojson_format.append([float(c) for c in coordinate])

        geojson = {'coordinates': points_geojson_format, 'type': 'LineString'}
        return super().validate(geojson, **kwargs)
