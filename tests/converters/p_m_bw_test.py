"""
Copyright 2024 binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

from pathlib import Path
from unittest.mock import Mock

import pytest
from requests_mock import Mocker

from parkapi_sources.converters import PMBWPullConverter
from parkapi_sources.util import RequestHelper
from tests.converters.helper import validate_realtime_parking_site_inputs, validate_static_parking_site_inputs


@pytest.fixture
def p_m_bw_config_helper(mocked_config_helper: Mock):
    config = {
        'PARK_API_P_M_BW_TOKEN': '127d24d7-8262-479c-8e22-c0d7e093b147',
        'STATIC_GEOJSON_BASE_URL': 'https://raw.githubusercontent.com/ParkenDD/parkapi-static-data/main/sources',
    }
    mocked_config_helper.get.side_effect = lambda key, default=None: config.get(key, default)
    return mocked_config_helper


@pytest.fixture
def p_m_bw_pull_converter(p_m_bw_config_helper: Mock, request_helper: RequestHelper) -> PMBWPullConverter:
    return PMBWPullConverter(config_helper=p_m_bw_config_helper, request_helper=request_helper)


class PMBWConverterTest:
    @staticmethod
    def test_get_static_parking_sites(p_m_bw_pull_converter: PMBWPullConverter, requests_mock: Mocker):
        # We need to get GeoJSON data
        requests_mock.real_http = True

        json_path = Path(Path(__file__).parent, 'data', 'p_m_bw.json')
        with json_path.open() as json_file:
            json_data = json_file.read()

        requests_mock.get('https://api.cloud-telartec.de/v1/parkings', text=json_data)

        static_parking_site_inputs, import_parking_site_exceptions = p_m_bw_pull_converter.get_static_parking_sites()

        assert len(static_parking_site_inputs) == 2
        assert len(import_parking_site_exceptions) == 0

        validate_static_parking_site_inputs(static_parking_site_inputs)

    @staticmethod
    def test_get_realtime_parking_sites(p_m_bw_pull_converter: PMBWPullConverter, requests_mock: Mocker):
        json_path = Path(Path(__file__).parent, 'data', 'p_m_bw.json')
        with json_path.open() as json_file:
            json_data = json_file.read()

        requests_mock.get('https://api.cloud-telartec.de/v1/parkings', text=json_data)

        static_parking_site_inputs, import_parking_site_exceptions = p_m_bw_pull_converter.get_realtime_parking_sites()

        assert len(static_parking_site_inputs) == 2
        assert len(import_parking_site_exceptions) == 0

        validate_realtime_parking_site_inputs(static_parking_site_inputs)
