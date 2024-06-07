"""
Copyright 2024 binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

from pathlib import Path
from unittest.mock import Mock

import pytest
from parkapi_sources.converters.apcoa import ApcoaPullConverter
from requests_mock import Mocker

from tests.converters.helper import validate_static_parking_site_inputs


@pytest.fixture
def apcoa_config_helper(mocked_config_helper: Mock):
    config = {
        'PARK_API_APCOA_API_SUBSCRIPTION_KEY': '9be98961de004749aac8a1d8160e9eba',
    }
    mocked_config_helper.get.side_effect = lambda key, default=None: config.get(key, default)
    return mocked_config_helper


@pytest.fixture
def apcoa_pull_converter(apcoa_config_helper: Mock) -> ApcoaPullConverter:
    return ApcoaPullConverter(config_helper=apcoa_config_helper)


class ApcoaPullConverterTest:
    @staticmethod
    def test_get_static_parking_sites(apcoa_pull_converter: ApcoaPullConverter, requests_mock: Mocker):
        json_path = Path(Path(__file__).parent, 'data', 'apcoa.json')
        with json_path.open() as json_file:
            json_data = json_file.read()

        requests_mock.get(
            'https://api.apcoa-services.com/carpark-dev/v4/Carparks',
            text=json_data,
        )

        static_parking_site_inputs, import_parking_site_exceptions = apcoa_pull_converter.get_static_parking_sites()

        assert len(static_parking_site_inputs) == 305
        assert len(import_parking_site_exceptions) == 264

        validate_static_parking_site_inputs(static_parking_site_inputs)
