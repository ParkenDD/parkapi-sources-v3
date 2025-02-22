"""
Copyright 2024 binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

from pathlib import Path
from unittest.mock import Mock

import pytest
from requests_mock import Mocker

from parkapi_sources.converters import AachenPullConverter, VrsVaihingenPullConverter
from parkapi_sources.util import RequestHelper
from tests.converters.helper import validate_realtime_parking_site_inputs, validate_static_parking_site_inputs


@pytest.fixture
def aachen_config_helper(mocked_config_helper: Mock):
    config = {
        'PARK_API_MOBILITHEK_CERT': '/dev/null',
        'PARK_API_MOBILITHEK_KEY': '/dev/null',
        'PARK_API_MOBILITHEK_AACHEN_STATIC_SUBSCRIPTION_ID': 1234567890,
        'PARK_API_MOBILITHEK_AACHEN_REALTIME_SUBSCRIPTION_ID': 1234567890,
    }
    mocked_config_helper.get.side_effect = lambda key, default=None: config.get(key, default)
    return mocked_config_helper


@pytest.fixture
def aachen_pull_converter(aachen_config_helper: Mock, request_helper: RequestHelper) -> AachenPullConverter:
    return AachenPullConverter(config_helper=aachen_config_helper, request_helper=request_helper)


class AachenConverterTest:
    @staticmethod
    def test_get_static_parking_sites(aachen_pull_converter: VrsVaihingenPullConverter, requests_mock: Mocker):
        xml_path = Path(Path(__file__).parent, 'data', 'aachen-static.xml')
        with xml_path.open() as xml_file:
            xml_data = xml_file.read()

        requests_mock.get(
            'https://mobilithek.info:8443/mobilithek/api/v1.0/subscription/1234567890/clientPullService?subscriptionID=1234567890',
            text=xml_data,
        )

        static_parking_site_inputs, import_parking_site_exceptions = aachen_pull_converter.get_static_parking_sites()

        assert len(static_parking_site_inputs) == 15
        assert len(import_parking_site_exceptions) == 2

        validate_static_parking_site_inputs(static_parking_site_inputs)

    @staticmethod
    def test_get_realtime_parking_sites(aachen_pull_converter: VrsVaihingenPullConverter, requests_mock: Mocker):
        xml_path = Path(Path(__file__).parent, 'data', 'aachen-realtime.xml')
        with xml_path.open() as xml_file:
            xml_data = xml_file.read()

        requests_mock.get(
            'https://mobilithek.info:8443/mobilithek/api/v1.0/subscription/1234567890/clientPullService?subscriptionID=1234567890',
            text=xml_data,
        )

        static_parking_site_inputs, import_parking_site_exceptions = aachen_pull_converter.get_realtime_parking_sites()

        assert len(static_parking_site_inputs) == 17
        assert len(import_parking_site_exceptions) == 0

        validate_realtime_parking_site_inputs(static_parking_site_inputs)
