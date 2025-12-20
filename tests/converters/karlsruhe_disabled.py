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
from tests.converters.helper import validate_realtime_parking_spot_inputs, validate_static_parking_spot_inputs


@pytest.fixture
def karlsruhe_disabled_pull_converter(
    mocked_config_helper: Mock,
    request_helper: RequestHelper,
) -> KarlsruheDisabledPullConverter:
    config = {'PARK_API_KARLSRUHE_DISABLED_AUTH': 'AUTH'}
    mocked_config_helper.get.side_effect = lambda key, default=None: config.get(key, default)
    return KarlsruheDisabledPullConverter(
        config_helper=mocked_config_helper,
        request_helper=request_helper,
    )


@pytest.fixture
def requests_mock_karlsruhe_disabled(requests_mock: Mocker) -> Mocker:
    static_json_path = Path(Path(__file__).parent, 'data', 'karlsruhe_disabled_static.geojson')
    with static_json_path.open() as static_json_file:
        static_json_data = static_json_file.read()

    realtime_json_path = Path(Path(__file__).parent, 'data', 'karlsruhe_disabled_realtime.json')
    with realtime_json_path.open() as realtime_json_file:
        realtime_json_data = realtime_json_file.read()

    requests_mock.get(
        'https://mobil.trk.de/geoserver/TBA/ows?service=WFS&version=1.0.0&request=GetFeature&srsname=EPSG:4326'
        '&typeName=TBA%3Abehinderten_parkplaetze&outputFormat=application%2Fjson',
        text=static_json_data,
    )

    requests_mock.get(
        'https://mobil.trk.de/swkiot/tags/c9ac643f-aedd-4794-83fb-7b7337744480/devices?limit=99&last_readings=1&auth=AUTH',
        text=realtime_json_data,
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

        assert len(static_parking_spot_inputs) == 1165
        assert len(import_parking_spot_exceptions) == 4

        validate_static_parking_spot_inputs(static_parking_spot_inputs)

    @staticmethod
    def test_get_realtime_parking_spots(
        karlsruhe_disabled_pull_converter: KarlsruheDisabledPullConverter,
        requests_mock_karlsruhe_disabled: Mocker,
    ):
        realtime_parking_spot_inputs, import_parking_spot_exceptions = (
            karlsruhe_disabled_pull_converter.get_realtime_parking_spots()
        )

        assert len(realtime_parking_spot_inputs) == 54
        assert len(import_parking_spot_exceptions) == 8

        validate_realtime_parking_spot_inputs(realtime_parking_spot_inputs)
