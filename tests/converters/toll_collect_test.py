"""
Copyright 2025 binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

from pathlib import Path
from unittest.mock import Mock

import pytest
from requests_mock import Mocker

from parkapi_sources.converters import TollCollectPullConverter
from parkapi_sources.util import RequestHelper
from tests.converters.helper import validate_realtime_parking_site_inputs, validate_static_parking_site_inputs


@pytest.fixture
def toll_collect_config_helper(mocked_config_helper: Mock):
    config = {
        'PARK_API_MOBILITHEK_CERT': '/dev/null',
        'PARK_API_MOBILITHEK_KEY': '/dev/null',
        'PARK_API_MOBILITHEK_TOLL_COLLECT_STATIC_SUBSCRIPTION_ID': 1111111111,
        'PARK_API_MOBILITHEK_TOLL_COLLECT_REALTIME_SUBSCRIPTION_ID': 2222222222,
    }
    mocked_config_helper.get.side_effect = lambda key, default=None: config.get(key, default)
    return mocked_config_helper


@pytest.fixture
def toll_collect_pull_converter(
    toll_collect_config_helper: Mock,
    request_helper: RequestHelper,
) -> TollCollectPullConverter:
    return TollCollectPullConverter(config_helper=toll_collect_config_helper, request_helper=request_helper)


class TollCollectConverterTest:
    @staticmethod
    def test_get_static_parking_sites(toll_collect_pull_converter: TollCollectPullConverter, requests_mock: Mocker):
        xml_path = Path(Path(__file__).parent, 'data', 'toll-collect-static.xml')
        with xml_path.open() as xml_file:
            xml_data = xml_file.read()

        requests_mock.get(
            'https://mobilithek.info:8443/mobilithek/api/v1.0/subscription/1111111111/clientPullService?subscriptionID=1111111111',
            text=xml_data,
        )

        static_parking_site_inputs, import_parking_site_exceptions = (
            toll_collect_pull_converter.get_static_parking_sites()
        )

        assert len(static_parking_site_inputs) > 0
        assert len(import_parking_site_exceptions) == 0

        validate_static_parking_site_inputs(static_parking_site_inputs)

    @staticmethod
    def test_get_realtime_parking_sites(toll_collect_pull_converter: TollCollectPullConverter, requests_mock: Mocker):
        static_xml_path = Path(Path(__file__).parent, 'data', 'toll-collect-static.xml')
        with static_xml_path.open() as xml_file:
            static_xml_data = xml_file.read()

        realtime_xml_path = Path(Path(__file__).parent, 'data', 'toll-collect-realtime.xml')
        with realtime_xml_path.open() as xml_file:
            realtime_xml_data = xml_file.read()

        # The realtime request fetches the static data as well, to calculate the free capacity
        requests_mock.get(
            'https://mobilithek.info:8443/mobilithek/api/v1.0/subscription/1111111111/clientPullService?subscriptionID=1111111111',
            text=static_xml_data,
        )
        requests_mock.get(
            'https://mobilithek.info:8443/mobilithek/api/v1.0/subscription/2222222222/clientPullService?subscriptionID=2222222222',
            text=realtime_xml_data,
        )

        realtime_parking_site_inputs, import_parking_site_exceptions = (
            toll_collect_pull_converter.get_realtime_parking_sites()
        )

        assert len(realtime_parking_site_inputs) > 0
        assert len(import_parking_site_exceptions) == 0

        # The free capacity is calculated from the static total capacity and the realtime occupied spaces
        assert any(item.realtime_free_capacity is not None for item in realtime_parking_site_inputs)

        validate_realtime_parking_site_inputs(realtime_parking_site_inputs)
