"""
Copyright 2026 binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

import pytest
from shapely import GeometryType, LineString, Point
from shapely.geometry.polygon import Polygon
from validataclass.exceptions import ValidationError

from parkapi_sources.validators.csv_geojson_geometry_validator import CsvGeoJSONGeometryValidator


@pytest.mark.parametrize(
    'input_data, output_data',
    [
        (
            'LINESTRING (9.4685377271586066 47.6516301483882998, 9.4685027073456922 47.6516177975497328)',
            LineString([[9.4685377271586066, 47.6516301483882998], [9.4685027073456922, 47.6516177975497328]]),
        ),
        (
            'POINT (7.846680277113961 47.992113179276828)',
            Point([7.846680277113961, 47.992113179276828]),
        ),
        (
            (
                'POLYGON ((7.794124176880983 48.001001703587214,  7.794146563630131 48.000992032946364,  '
                '7.794106121803726 48.000949864383301,  7.794083735065564 48.00095953501642,  '
                '7.794124176880983 48.001001703587214))'
            ),
            Polygon([
                [7.794124176880983, 48.001001703587214],
                [7.794146563630131, 48.000992032946364],
                [7.794106121803726, 48.000949864383301],
                [7.794083735065564, 48.00095953501642],
                [7.794124176880983, 48.001001703587214],
            ]),
        ),
    ],
)
def test_csv_geojson_geometry_validator_success(
    input_data: str,
    output_data: LineString,
):
    validator = CsvGeoJSONGeometryValidator(allowed_geometry_types=[GeometryType.LINESTRING])

    assert validator.validate(input_data) == output_data


def test_csv_geojson_geometry_validator_fails():
    validator = CsvGeoJSONGeometryValidator(allowed_geometry_types=[GeometryType.LINESTRING])

    with pytest.raises(ValidationError) as error:
        validator.validate('LINESTRING (9 47, 9 47)')

    assert error.value.code == 'invalid_input_data_type'
    assert error.value.reason == 'Geometry is not valid'
