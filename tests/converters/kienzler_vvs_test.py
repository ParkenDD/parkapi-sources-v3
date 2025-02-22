"""
Copyright 2024 binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

from pathlib import Path
from unittest.mock import Mock

import pytest
from requests_mock import Mocker

from parkapi_sources.converters import KienzlerVVSPullConverter
from parkapi_sources.util import RequestHelper
from tests.converters.helper import validate_realtime_parking_site_inputs, validate_static_parking_site_inputs


@pytest.fixture
def requests_mock_kienzler_vvs(requests_mock: Mocker) -> Mocker:
    json_path = Path(Path(__file__).parent, 'data', 'kienzler_vvs.json')
    with json_path.open() as json_file:
        json_data = json_file.read()

    requests_mock.post('https://vvs.bike-and-park.de/index.php', text=json_data)

    return requests_mock


@pytest.fixture
def kienzler_config_helper(mocked_config_helper: Mock):
    config = {
        'PARK_API_KIENZLER_VVS_USER': '01275925-742c-460b-8778-eca90eb114bc',
        'PARK_API_KIENZLER_VVS_PASSWORD': '626027f2-66e9-40bd-8ff2-4c010f5eca05',
        'PARK_API_KIENZLER_VVS_IDS': 'id1,id2,id3',
    }
    mocked_config_helper.get.side_effect = lambda key, default=None: config.get(key, default)
    return mocked_config_helper


@pytest.fixture
def kienzler_vvs_pull_converter(
    kienzler_config_helper: Mock,
    request_helper: RequestHelper,
) -> KienzlerVVSPullConverter:
    return KienzlerVVSPullConverter(config_helper=kienzler_config_helper, request_helper=request_helper)


class KienzlerVVSPullConverterTest:
    @staticmethod
    def test_get_static_parking_sites(
        kienzler_vvs_pull_converter: KienzlerVVSPullConverter,
        requests_mock_kienzler_vvs: Mocker,
    ):
        static_parking_site_inputs, import_parking_site_exceptions = (
            kienzler_vvs_pull_converter.get_static_parking_sites()
        )

        assert len(static_parking_site_inputs) == 2
        assert len(import_parking_site_exceptions) == 0

        validate_static_parking_site_inputs(static_parking_site_inputs)

    @staticmethod
    def test_get_realtime_parking_sites(
        kienzler_vvs_pull_converter: KienzlerVVSPullConverter,
        requests_mock_kienzler_vvs: Mocker,
    ):
        realtime_parking_site_inputs, import_parking_site_exceptions = (
            kienzler_vvs_pull_converter.get_realtime_parking_sites()
        )

        assert len(realtime_parking_site_inputs) == 2
        assert len(import_parking_site_exceptions) == 0

        validate_realtime_parking_site_inputs(realtime_parking_site_inputs)
