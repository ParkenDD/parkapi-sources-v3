"""
Copyright 2024 binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

from pathlib import Path
from unittest.mock import Mock

import pytest
from requests_mock import Mocker

from parkapi_sources.converters.heidelberg import HeidelbergPullConverter
from parkapi_sources.util import RequestHelper
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
def heidelberg_pull_converter(heidelberg_config_helper: Mock, request_helper: RequestHelper) -> HeidelbergPullConverter:
    return HeidelbergPullConverter(config_helper=heidelberg_config_helper, request_helper=request_helper)


@pytest.fixture
def heidelberg_request_mock(requests_mock: Mock):
    json_path = Path(Path(__file__).parent, 'data', 'heidelberg.json')
    with json_path.open() as json_file:
        json_data = json_file.read()

    requests_mock.get(
        'https://api.datenplattform.heidelberg.de/ckan/or/mobility/main/offstreetparking/v2/entities',
        text=json_data,
    )

    return requests_mock


class HeidelbergPullConverterTest:
    @staticmethod
    def test_get_static_parking_sites(
        heidelberg_pull_converter: HeidelbergPullConverter, heidelberg_request_mock: Mocker
    ):
        static_parking_site_inputs, import_parking_site_exceptions = (
            heidelberg_pull_converter.get_static_parking_sites()
        )

        assert len(static_parking_site_inputs) == 22
        assert len(import_parking_site_exceptions) == 3

        validate_static_parking_site_inputs(static_parking_site_inputs)

    @staticmethod
    def test_get_realtime_parking_sites(
        heidelberg_pull_converter: HeidelbergPullConverter, heidelberg_request_mock: Mocker
    ):
        realtime_parking_site_inputs, import_parking_site_exceptions = (
            heidelberg_pull_converter.get_realtime_parking_sites()
        )

        assert len(realtime_parking_site_inputs) == 20  # Two parking sites don't have a realtime status
        assert len(import_parking_site_exceptions) == 3

        validate_realtime_parking_site_inputs(realtime_parking_site_inputs)
