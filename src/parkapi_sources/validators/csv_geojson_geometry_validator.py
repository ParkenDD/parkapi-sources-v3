"""
Copyright 2026 binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

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
            raise ValidationError(reason='CsvGeoJSONGeometryValidator only supports LINESTRING')
        super().__init__(allowed_geometry_types, **kwargs)

    @override
    def validate(self, input_data: Any, **kwargs: Any) -> BaseGeometry:
        if type(input_data) is not str:
            raise ValidationError(reason='Wrong datatype found for CsvGeoJSONGeometryValidator')

        input_data = input_data.replace('LINESTRING (', '')
        input_data = input_data.replace(')', '')
        points = input_data.split(',')
        points_geo_str = []
        for point in points:
            point = point.strip()
            coordinate = point.split(' ')
            points_geo_str.append([float(c) for c in coordinate])

        points_geo_json = {'coordinates': points_geo_str, 'type': 'LineString'}
        return super().validate(points_geo_json, **kwargs)
