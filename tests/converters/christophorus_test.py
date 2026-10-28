"""
Copyright 2026 binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

from unittest.mock import Mock

import pytest
from requests_mock import Mocker

from parkapi_sources.converters import ChristophorusPullConverter
from parkapi_sources.util import RequestHelper
from tests.converters.helper import get_data_path


@pytest.fixture
def christophorus_config_helper(mocked_config_helper: Mock):
    config = {
        'PARK_API_MOBILITHEK_CERT': '/dev/null',
        'PARK_API_MOBILITHEK_KEY': '/dev/null',
        'PARK_API_MOBILITHEK_CHRISTOPHORUS_STATIC_SUBSCRIPTION_ID': 1111111111,
        'PARK_API_MOBILITHEK_CHRISTOPHORUS_REALTIME_SUBSCRIPTION_ID': 2222222222,
    }
    mocked_config_helper.get.side_effect = lambda key, default=None: config.get(key, default)
    return mocked_config_helper


@pytest.fixture
def christophorus_pull_converter(
    christophorus_config_helper: Mock,
    request_helper: RequestHelper,
) -> ChristophorusPullConverter:
    return ChristophorusPullConverter(config_helper=christophorus_config_helper, request_helper=request_helper)


class ChristophorusPullConverterTest:
    @staticmethod
    def test_get_static_parking_sites(
        christophorus_pull_converter: ChristophorusPullConverter,
        requests_mock: Mocker,
    ):
        requests_mock.get(
            'https://mobilithek.info:8443/mobilithek/api/v1.0/subscription/datexv3?subscriptionID=1111111111',
            text=get_data_path('christophorus-static.xml').read_text(),
        )

        static_parking_site_inputs, import_parking_site_exceptions = (
            christophorus_pull_converter.get_static_parking_sites()
        )

        # The payload is wrapped in a messageContainer, which is not part of the declared profile
        assert len(static_parking_site_inputs) == 0
        assert len(import_parking_site_exceptions) == 1
        assert 'messageContainer' in import_parking_site_exceptions[0].message

    @staticmethod
    def test_get_realtime_parking_sites(
        christophorus_pull_converter: ChristophorusPullConverter,
        requests_mock: Mocker,
    ):
        requests_mock.get(
            'https://mobilithek.info:8443/mobilithek/api/v1.0/subscription/datexv3?subscriptionID=2222222222',
            text=get_data_path('christophorus-realtime.xml').read_text(),
        )

        realtime_parking_site_inputs, import_parking_site_exceptions = (
            christophorus_pull_converter.get_realtime_parking_sites()
        )

        assert len(realtime_parking_site_inputs) == 0
        assert len(import_parking_site_exceptions) == 1
        assert 'messageContainer' in import_parking_site_exceptions[0].message
