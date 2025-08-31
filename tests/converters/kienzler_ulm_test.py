"""
Copyright 2024 binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

from pathlib import Path
from unittest.mock import Mock

import pytest
from requests_mock import Mocker

from parkapi_sources.converters import KienzlerUlmPullConverter
from parkapi_sources.util import RequestHelper
from tests.converters.helper import validate_realtime_parking_site_inputs, validate_static_parking_site_inputs


@pytest.fixture
def requests_mock_kienzler_ulm(requests_mock: Mocker) -> Mocker:
    json_path = Path(Path(__file__).parent, 'data', 'kienzler_ulm.json')
    with json_path.open() as json_file:
        json_data = json_file.read()

    requests_mock.get('https://ulm.bike-and-park.de/api/v1/capacity/units/all', text=json_data)

    return requests_mock


@pytest.fixture
def kienzler_config_helper(mocked_config_helper: Mock):
    config = {
        'PARK_API_KIENZLER_ULM_USER': '01275925-742c-460b-8778-eca90eb114bc',
        'PARK_API_KIENZLER_ULM_PASSWORD': '626027f2-66e9-40bd-8ff2-4c010f5eca05',
    }
    mocked_config_helper.get.side_effect = lambda key, default=None: config.get(key, default)
    return mocked_config_helper


@pytest.fixture
def kienzler_ulm_pull_converter(
    kienzler_config_helper: Mock,
    request_helper: RequestHelper,
) -> KienzlerUlmPullConverter:
    return KienzlerUlmPullConverter(config_helper=kienzler_config_helper, request_helper=request_helper)


class KienzlerULMPullConverterTest:
    @staticmethod
    def test_get_static_parking_sites(
        kienzler_ulm_pull_converter: KienzlerUlmPullConverter,
        requests_mock_kienzler_ulm: Mocker,
    ):
        static_parking_site_inputs, import_parking_site_exceptions = (
            kienzler_ulm_pull_converter.get_static_parking_sites()
        )

        assert len(static_parking_site_inputs) == 6
        assert len(import_parking_site_exceptions) == 0

        validate_static_parking_site_inputs(static_parking_site_inputs)

    @staticmethod
    def test_get_realtime_parking_sites(
        kienzler_ulm_pull_converter: KienzlerUlmPullConverter,
        requests_mock_kienzler_ulm: Mocker,
    ):
        realtime_parking_site_inputs, import_parking_site_exceptions = (
            kienzler_ulm_pull_converter.get_realtime_parking_sites()
        )

        assert len(realtime_parking_site_inputs) == 6
        assert len(import_parking_site_exceptions) == 0

        validate_realtime_parking_site_inputs(realtime_parking_site_inputs)
