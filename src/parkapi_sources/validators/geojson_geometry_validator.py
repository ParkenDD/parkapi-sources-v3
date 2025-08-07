"""
Copyright 2025 binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

import json
from typing import Any

import pyproj
from shapely import GeometryType, GEOSException, from_geojson, get_type_id, transform
from shapely.geometry.base import BaseGeometry
from validataclass.exceptions import ValidationError
from validataclass.validators import Validator


class InvalidGeoJSONGeometryError(ValidationError):
    code = 'invalid_geojson_geometry'


class GeoJSONGeometryValidator(Validator):
    allowed_geometry_types: list[GeometryType] | None
    projection: pyproj.Proj | None

    def __init__(
        self,
        allowed_geometry_types: list[GeometryType] | None = None,
        projection: pyproj.Proj | None = None,
        **kwargs,
    ):
        super().__init__(**kwargs)
        self.allowed_geometry_types = allowed_geometry_types
        self.projection = projection

    def validate(self, input_data: Any, **kwargs: Any) -> BaseGeometry:
        try:
            geometry = from_geojson(json.dumps(input_data))
        except GEOSException as e:
            raise InvalidGeoJSONGeometryError(reason='Invalid GeoJSON geometry') from e

        if geometry.is_empty:
            raise InvalidGeoJSONGeometryError(reason='Empty GeoJSON geometry')

        if self.allowed_geometry_types and GeometryType(get_type_id(geometry)) not in self.allowed_geometry_types:
            raise InvalidGeoJSONGeometryError(reason='Invalid geometgry type')

        if self.projection is not None:
            geometry = transform(geometry, lambda *args: self.projection(*args, inverse=True), interleaved=False)

        return geometry
