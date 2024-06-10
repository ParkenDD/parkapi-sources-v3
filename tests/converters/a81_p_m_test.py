"""
Copyright 2024 binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

from pathlib import Path
from unittest.mock import Mock

import pytest
from parkapi_sources.converters import A81PMPullConverter
from requests_mock import Mocker

from tests.converters.helper import validate_realtime_parking_site_inputs, validate_static_parking_site_inputs


@pytest.fixture
def a81_p_m_config_helper(mocked_config_helper: Mock):
    config = {
        'PARK_API_A81_P_M_TOKEN': '127d24d7-8262-479c-8e22-c0d7e093b147',
    }
    mocked_config_helper.get.side_effect = lambda key, default=None: config.get(key, default)
    return mocked_config_helper


@pytest.fixture
def a81_p_m_pull_converter(a81_p_m_config_helper: Mock) -> A81PMPullConverter:
    return A81PMPullConverter(config_helper=a81_p_m_config_helper)


class A81PMConverterTest:
    @staticmethod
    def test_get_static_parking_sites(a81_p_m_pull_converter: A81PMPullConverter, requests_mock: Mocker):
        json_path = Path(Path(__file__).parent, 'data', 'a81_p_m.json')
        with json_path.open() as json_file:
            json_data = json_file.read()

        requests_mock.get('https://api.cloud-telartec.de/v1/parkings', text=json_data)

        static_parking_site_inputs, import_parking_site_exceptions = a81_p_m_pull_converter.get_static_parking_sites()

        assert len(static_parking_site_inputs) == 2
        assert len(import_parking_site_exceptions) == 0

        validate_static_parking_site_inputs(static_parking_site_inputs)

    @staticmethod
    def test_get_realtime_parking_sites(a81_p_m_pull_converter: A81PMPullConverter, requests_mock: Mocker):
        json_path = Path(Path(__file__).parent, 'data', 'a81_p_m.json')
        with json_path.open() as json_file:
            json_data = json_file.read()

        requests_mock.get('https://api.cloud-telartec.de/v1/parkings', text=json_data)

        static_parking_site_inputs, import_parking_site_exceptions = a81_p_m_pull_converter.get_realtime_parking_sites()

        assert len(static_parking_site_inputs) == 2
        assert len(import_parking_site_exceptions) == 0

        validate_realtime_parking_site_inputs(static_parking_site_inputs)
