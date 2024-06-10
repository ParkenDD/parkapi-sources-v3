"""
Copyright 2024 binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

from pathlib import Path
from unittest.mock import Mock

import pytest
from parkapi_sources.converters.heidelberg import HeidelbergPullConverter
from requests_mock import Mocker

from tests.converters.helper import validate_realtime_parking_site_inputs, validate_static_parking_site_inputs


@pytest.fixture
def heidelberg_config_helper(mocked_config_helper: Mock):
    config = {
        'STATIC_GEOJSON_BASE_URL': 'https://raw.githubusercontent.com/ParkenDD/parkapi-static-data/main/sources',
        'PARK_API_HEIDELBERG_API_KEY': '2fced81b-ec5e-43f9-aa9c-0d12731a7813',
    }
    mocked_config_helper.get.side_effect = lambda key, default=None: config.get(key, default)
    return mocked_config_helper


@pytest.fixture
def heidelberg_pull_converter(heidelberg_config_helper: Mock) -> HeidelbergPullConverter:
    return HeidelbergPullConverter(config_helper=heidelberg_config_helper)


class HeidelbergPullConverterTest:
    @staticmethod
    def test_get_static_parking_sites(heidelberg_pull_converter: HeidelbergPullConverter):
        static_parking_site_inputs, import_parking_site_exceptions = heidelberg_pull_converter.get_static_parking_sites()
        assert len(static_parking_site_inputs) > len(
            import_parking_site_exceptions
        ), 'There should be more valid then invalid parking sites'

        validate_static_parking_site_inputs(static_parking_site_inputs)

    @staticmethod
    def test_get_realtime_parking_sites(heidelberg_pull_converter: HeidelbergPullConverter, requests_mock: Mocker):
        json_path = Path(Path(__file__).parent, 'data', 'heidelberg.json')
        with json_path.open() as json_file:
            json_data = json_file.read()

        requests_mock.get('https://parken.heidelberg.de/v1/parking-update', text=json_data)

        realtime_parking_site_inputs, import_parking_site_exceptions = heidelberg_pull_converter.get_realtime_parking_sites()

        assert len(realtime_parking_site_inputs) == 21
        assert len(import_parking_site_exceptions) == 0

        validate_realtime_parking_site_inputs(realtime_parking_site_inputs)
