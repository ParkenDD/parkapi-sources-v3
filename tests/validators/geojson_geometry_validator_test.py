"""
Copyright 2025 binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

from datetime import date
from typing import Any

import pyproj
import pytest
from shapely import GeometryType, LineString, Point
from shapely.geometry.polygon import Polygon
from validataclass.exceptions import ValidationError

from parkapi_sources.validators import GeoJSONGeometryValidator


@pytest.mark.parametrize(
    'allowed_geometry_types, projection, input_data, output_data',
    [
        (None, None, {'type': 'Point', 'coordinates': [10.0, 50.0]}, Point(10.0, 50.0)),
        (
            None,
            None,
            {
                'type': 'Polygon',
                'coordinates': [
                    [
                        [7.834144, 47.999896],
                        [7.834203, 47.999874],
                        [7.834190, 47.9998],
                        [7.834131, 47.999880],
                        [7.834144, 47.999896],
                    ],
                ],
            },
            Polygon(
                [
                    [7.834144, 47.999896],
                    [7.834203, 47.999874],
                    [7.834190, 47.9998],
                    [7.834131, 47.999880],
                    [7.834144, 47.999896],
                ],
            ),
        ),
        (
            None,
            None,
            {
                'type': 'LineString',
                'coordinates': [
                    [477594.12, 5474162.70],
                    [477592.20, 5474162.16],
                    [477590.27, 5474161.61],
                    [477588.35, 5474161.06],
                    [477586.43, 5474160.51],
                    [477583.88, 5474159.79],
                ],
            },
            LineString(
                [
                    [477594.12, 5474162.70],
                    [477592.20, 5474162.16],
                    [477590.27, 5474161.61],
                    [477588.35, 5474161.06],
                    [477586.43, 5474160.51],
                    [477583.88, 5474159.79],
                ],
            ),
        ),
        (
            None,
            None,
            {
                'type': 'LineString',
                'coordinates': [
                    [477594.12, 5474162.70],
                    [477592.20, 5474162.16],
                    [477590.27, 5474161.61],
                    [477588.35, 5474161.06],
                    [477586.43, 5474160.51],
                    [477583.88, 5474159.79],
                ],
            },
            LineString(
                [
                    [477594.12, 5474162.70],
                    [477592.20, 5474162.16],
                    [477590.27, 5474161.61],
                    [477588.35, 5474161.06],
                    [477586.43, 5474160.51],
                    [477583.88, 5474159.79],
                ],
            ),
        ),
        ([GeometryType.POINT], None, {'type': 'Point', 'coordinates': [10.0, 50.0]}, Point(10.0, 50.0)),
        (
            None,
            pyproj.Proj(proj='utm', zone=32, ellps='WGS84', preserve_units=True),
            {
                'type': 'LineString',
                'coordinates': [
                    [477594.12, 5474162.70],
                    [477592.20, 5474162.16],
                    [477590.27, 5474161.61],
                    [477588.35, 5474161.06],
                    [477586.43, 5474160.51],
                    [477583.88, 5474159.79],
                ],
            },
            LineString(
                [
                    [8.691063712218511, 49.41972949419808],
                    [8.691037269812888, 49.419724566263156],
                    [8.691010690097675, 49.4197195480055],
                    [8.690984248267545, 49.41971453011018],
                    [8.690957806442837, 49.419709512208826],
                    [8.690922687811387, 49.41970294196387],
                ],
            ),
        ),
    ],
)
def test_geojson_geometry_validator_success(
    allowed_geometry_types: list[GeometryType] | None,
    projection: pyproj.Proj | None,
    input_data: Any,
    output_data: date,
):
    validator = GeoJSONGeometryValidator(allowed_geometry_types=allowed_geometry_types, projection=projection)

    assert validator.validate(input_data) == output_data


@pytest.mark.parametrize(
    'allowed_geometry_types, input_data',
    [
        (None, {}),
        (None, {'type': 'Point', 'coordinates': []}),
        # Polygon which is not closed
        (
            None,
            {
                'type': 'Polygon',
                'coordinates': [
                    [
                        [7.834144, 47.999896],
                        [7.834203, 47.999874],
                        [7.834190, 47.9998],
                        [7.834131, 47.999880],
                    ],
                ],
            },
        ),
        ([GeometryType.LINESTRING], {'type': 'Point', 'coordinates': [10.0, 50.0]}),
    ],
)
def test_geojson_geometry_validator_fail(allowed_geometry_types: list[GeometryType] | None, input_data: Any):
    validator = GeoJSONGeometryValidator(allowed_geometry_types=allowed_geometry_types)

    with pytest.raises(ValidationError):
        validator.validate(input_data)
