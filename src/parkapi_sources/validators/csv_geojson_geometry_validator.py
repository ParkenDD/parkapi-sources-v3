"""
Copyright 2026 binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

from typing import Any, override

import shapely
from shapely.geometry.base import BaseGeometry
from validataclass.exceptions import ValidationError

from parkapi_sources.validators import GeoJSONGeometryValidator


class CsvGeoJSONGeometryValidator(GeoJSONGeometryValidator):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    @override
    def validate(self, input_data: str, **kwargs: Any) -> BaseGeometry:
        geometry: BaseGeometry = shapely.from_wkt(input_data)
        if not geometry.is_valid:
            raise ValidationError(code='invalid_input_data_type', reason='Geometry is not valid')
        return geometry
