"""
Copyright 2025 binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

from pathlib import Path
from unittest.mock import Mock

import pytest
from requests_mock import Mocker

from parkapi_sources.converters import BietigheimBissingenDatexPullConverter
from parkapi_sources.util import RequestHelper
from tests.converters.helper import validate_realtime_parking_site_inputs, validate_static_parking_site_inputs


@pytest.fixture
def bietigheim_bissingen_config_helper(mocked_config_helper: Mock):
    config = {
        'PARK_API_MOBILITHEK_CERT': '/dev/null',
        'PARK_API_MOBILITHEK_KEY': '/dev/null',
        'PARK_API_MOBILITHEK_BIETIGHEIM_BISSINGEN_STATIC_SUBSCRIPTION_ID': 1234567890,
        'PARK_API_MOBILITHEK_BIETIGHEIM_BISSINGEN_REALTIME_SUBSCRIPTION_ID': 1234567890,
    }
    mocked_config_helper.get.side_effect = lambda key, default=None: config.get(key, default)
    return mocked_config_helper


@pytest.fixture
def bietigheim_bissingen_pull_converter(
    bietigheim_bissingen_config_helper: Mock, request_helper: RequestHelper
) -> BietigheimBissingenDatexPullConverter:
    return BietigheimBissingenDatexPullConverter(
        config_helper=bietigheim_bissingen_config_helper, request_helper=request_helper
    )


class BietigheimBissingenConverterTest:
    @staticmethod
    def test_get_static_parking_sites(
        bietigheim_bissingen_pull_converter: BietigheimBissingenDatexPullConverter, requests_mock: Mocker
    ):
        xml_path = Path(Path(__file__).parent, 'data', 'bietigheim_bissingen_static.xml')
        with xml_path.open() as xml_file:
            xml_data = xml_file.read()

        requests_mock.get(
            'https://mobilithek.info:8443/mobilithek/api/v1.0/subscription/1234567890/clientPullService?subscriptionID=1234567890',
            text=xml_data,
        )

        static_parking_site_inputs, import_parking_site_exceptions = (
            bietigheim_bissingen_pull_converter.get_static_parking_sites()
        )

        assert len(static_parking_site_inputs) == 2
        assert len(import_parking_site_exceptions) == 0

        validate_static_parking_site_inputs(static_parking_site_inputs)

    @staticmethod
    def test_get_realtime_parking_sites(
        bietigheim_bissingen_pull_converter: BietigheimBissingenDatexPullConverter, requests_mock: Mocker
    ):
        xml_path = Path(Path(__file__).parent, 'data', 'bietigheim_bissingen_realtime.xml')
        with xml_path.open() as xml_file:
            xml_data = xml_file.read()

        requests_mock.get(
            'https://mobilithek.info:8443/mobilithek/api/v1.0/subscription/1234567890/clientPullService?subscriptionID=1234567890',
            text=xml_data,
        )

        static_parking_site_inputs, import_parking_site_exceptions = (
            bietigheim_bissingen_pull_converter.get_realtime_parking_sites()
        )

        assert len(static_parking_site_inputs) == 2
        assert len(import_parking_site_exceptions) == 0

        validate_realtime_parking_site_inputs(static_parking_site_inputs)
