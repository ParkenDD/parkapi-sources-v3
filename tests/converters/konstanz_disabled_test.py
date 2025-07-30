"""
Copyright 2025 binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

from pathlib import Path
from unittest.mock import Mock

import pytest
from requests_mock import Mocker

from parkapi_sources.converters import KonstanzDisabledPullConverter
from parkapi_sources.util import RequestHelper
from tests.converters.helper import validate_static_parking_spot_inputs


@pytest.fixture
def konstanz_disabled_pull_converter(
    mocked_config_helper: Mock,
    request_helper: RequestHelper,
) -> KonstanzDisabledPullConverter:
    return KonstanzDisabledPullConverter(
        config_helper=mocked_config_helper,
        request_helper=request_helper,
    )


class KonstanzDisabledConverterTest:
    @staticmethod
    def test_get_static_parking_spots(
        konstanz_disabled_pull_converter: KonstanzDisabledPullConverter,
        requests_mock: Mocker,
    ):
        json_path = Path(Path(__file__).parent, 'data', 'konstanz_disabled.geojson')
        with json_path.open() as json_file:
            json_data = json_file.read()

        requests_mock.get(
            'https://services-eu1.arcgis.com/cgMeYTGtzFtnxdsx/arcgis/rest/services/POI_Verkehr/FeatureServer/5'
            '/query?outFields=*&where=1%3D1&f=geojson',
            text=json_data,
        )

        static_parking_spot_inputs, import_parking_spot_exceptions = (
            konstanz_disabled_pull_converter.get_static_parking_spots()
        )
        result = []
        for static_parking_spot_input in static_parking_spot_inputs:
            result.append({
                'type': 'Feature',
                'properties': {'uid': static_parking_spot_input.uid},
                'geometry': {
                    'type': 'Point',
                    'coordinates': [float(static_parking_spot_input.lon), float(static_parking_spot_input.lat)],
                },
            })

        assert len(static_parking_spot_inputs) == 97
        assert len(import_parking_spot_exceptions) == 0

        validate_static_parking_spot_inputs(static_parking_spot_inputs)
