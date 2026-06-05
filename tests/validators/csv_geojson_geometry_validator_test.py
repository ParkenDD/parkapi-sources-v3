"""
Copyright 2026 binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

import pytest
from shapely import GeometryType, LineString
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
            '9.4685377271586066 47.6516301483882998, 9.4685027073456922 47.6516177975497328',
            LineString([[9.4685377271586066, 47.6516301483882998], [9.4685027073456922, 47.6516177975497328]]),
        ),
    ],
)
def test_csv_geojson_geometry_validator_success(
    input_data: str,
    output_data: LineString,
):
    validator = CsvGeoJSONGeometryValidator(allowed_geometry_types=[GeometryType.LINESTRING])

    assert validator.validate(input_data) == output_data


@pytest.mark.parametrize(
    'allowed_geometry_types',
    [
        [GeometryType.MULTIPOINT],
        [GeometryType.POLYGON, GeometryType.LINESTRING],
    ],
)
def test_csv_geojson_geometry_validator_init_fails(
    allowed_geometry_types: str,
):
    with pytest.raises(ValidationError) as error:
        CsvGeoJSONGeometryValidator(allowed_geometry_types=allowed_geometry_types)

    assert error.value.code == 'unsupported_geometry_type'
    assert error.value.reason == 'CsvGeoJSONGeometryValidator only supports LINESTRING'


@pytest.mark.parametrize(
    'input_data, error_code, error_message',
    [
        ('LINESTRING (9 47, 9 47)', 'invalid_geojson_geometry', 'Empty GeoJSON geometry'),
        ('9.4685377271586066 47.6516301483882998', 'invalid_geojson_geometry', 'Invalid GeoJSON geometry'),
        (
            [[9.4685377271586066, 47.6516301483882998], [9.4685027073456922, 47.6516177975497328]],
            'invalid_input_data_type',
            'Wrong datatype found for CsvGeoJSONGeometryValidator',
        ),
    ],
)
def test_csv_geojson_geometry_validator_fails(
    input_data: str,
    error_code: str,
    error_message: str,
):
    validator = CsvGeoJSONGeometryValidator(allowed_geometry_types=[GeometryType.LINESTRING])

    with pytest.raises(ValidationError) as error:
        validator.validate(input_data)

    assert error.value.code == error_code
    assert error.value.reason == error_message
