"""
Copyright 2024 binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

from pathlib import Path
from unittest.mock import Mock

import pytest
from requests_mock import Mocker

from parkapi_sources.converters.velobrix import VelobrixPullConverter
from parkapi_sources.util import RequestHelper
from tests.converters.helper import validate_realtime_parking_site_inputs, validate_static_parking_site_inputs


@pytest.fixture
def velobrix_config_helper(mocked_config_helper: Mock):
    config = {
        'STATIC_GEOJSON_BASE_URL': 'https://raw.githubusercontent.com/ParkenDD/parkapi-static-data/main/sources',
        'PARK_API_VELOBRIX_API_KEY': '2fced81b-ec5e-43f9-aa9c-0d12731a7813',
    }
    mocked_config_helper.get.side_effect = lambda key, default=None: config.get(key, default)
    return mocked_config_helper


@pytest.fixture
def velobrix_pull_converter(velobrix_config_helper: Mock, request_helper: RequestHelper) -> VelobrixPullConverter:
    return VelobrixPullConverter(config_helper=velobrix_config_helper, request_helper=request_helper)


@pytest.fixture
def velobrix_request_mock(requests_mock: Mock):
    json_path = Path(Path(__file__).parent, 'data', 'velobrix.json')
    with json_path.open() as json_file:
        json_data = json_file.read()

    requests_mock.get(
        'https://admin.velobrix.de/tenantapi/api/v1/locations',
        text=json_data,
    )

    return requests_mock


class VelobrixPullConverterTest:
    @staticmethod
    def test_get_static_parking_sites(velobrix_pull_converter: VelobrixPullConverter, velobrix_request_mock: Mocker):
        static_parking_site_inputs, import_parking_site_exceptions = velobrix_pull_converter.get_static_parking_sites()

        assert len(static_parking_site_inputs) == 3
        assert len(import_parking_site_exceptions) == 0

        validate_static_parking_site_inputs(static_parking_site_inputs)

    @staticmethod
    def test_get_realtime_parking_sites(velobrix_pull_converter: VelobrixPullConverter, velobrix_request_mock: Mocker):
        realtime_parking_site_inputs, import_parking_site_exceptions = (
            velobrix_pull_converter.get_realtime_parking_sites()
        )

        assert len(realtime_parking_site_inputs) == 3
        assert len(import_parking_site_exceptions) == 0

        validate_realtime_parking_site_inputs(realtime_parking_site_inputs)
