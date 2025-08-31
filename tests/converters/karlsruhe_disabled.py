"""
Copyright 2025 binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

from pathlib import Path
from unittest.mock import Mock

import pytest
from requests_mock import Mocker

from parkapi_sources.converters import KarlsruheDisabledPullConverter
from parkapi_sources.util import RequestHelper
from tests.converters.helper import validate_static_parking_spot_inputs


@pytest.fixture
def karlsruhe_disabled_pull_converter(
    mocked_config_helper: Mock,
    request_helper: RequestHelper,
) -> KarlsruheDisabledPullConverter:
    return KarlsruheDisabledPullConverter(
        config_helper=mocked_config_helper,
        request_helper=request_helper,
    )


@pytest.fixture
def requests_mock_karlsruhe_disabled(requests_mock: Mocker) -> Mocker:
    json_path = Path(Path(__file__).parent, 'data', 'karlsruhe_disabled.geojson')
    with json_path.open() as json_file:
        json_data = json_file.read()

    requests_mock.get(
        'https://mobil.trk.de/geoserver/TBA/ows?service=WFS&version=1.0.0&request=GetFeature&srsname=EPSG:4326'
        '&typeName=TBA%3Abehinderten_parkplaetze&outputFormat=application%2Fjson',
        text=json_data,
    )

    return requests_mock


class KarlsruheDisabledConverterTest:
    @staticmethod
    def test_get_static_parking_spots(
        karlsruhe_disabled_pull_converter: KarlsruheDisabledPullConverter,
        requests_mock_karlsruhe_disabled: Mocker,
    ):
        static_parking_spot_inputs, import_parking_spot_exceptions = (
            karlsruhe_disabled_pull_converter.get_static_parking_spots()
        )

        assert len(static_parking_spot_inputs) == 1166
        assert len(import_parking_spot_exceptions) == 0

        validate_static_parking_spot_inputs(static_parking_spot_inputs)
