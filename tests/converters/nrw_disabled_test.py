"""
Copyright 2026 binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

from unittest.mock import Mock

import pytest
from requests_mock import Mocker

from parkapi_sources.converters import NrwDisabledPullConverter
from parkapi_sources.util import RequestHelper
from tests.converters.helper import get_data_path


@pytest.fixture
def nrw_disabled_config_helper(mocked_config_helper: Mock):
    config = {
        'PARK_API_MOBILITHEK_CERT': '/dev/null',
        'PARK_API_MOBILITHEK_KEY': '/dev/null',
        'PARK_API_MOBILITHEK_NRW_DISABLED_STATIC_SUBSCRIPTION_ID': 1111111111,
    }
    mocked_config_helper.get.side_effect = lambda key, default=None: config.get(key, default)
    return mocked_config_helper


@pytest.fixture
def nrw_disabled_pull_converter(
    nrw_disabled_config_helper: Mock,
    request_helper: RequestHelper,
) -> NrwDisabledPullConverter:
    return NrwDisabledPullConverter(config_helper=nrw_disabled_config_helper, request_helper=request_helper)


class NrwDisabledPullConverterTest:
    @staticmethod
    def test_required_config_keys(nrw_disabled_pull_converter: NrwDisabledPullConverter):
        # Without realtime data, there is no realtime subscription
        assert nrw_disabled_pull_converter.required_config_keys == [
            'PARK_API_MOBILITHEK_CERT',
            'PARK_API_MOBILITHEK_KEY',
            'PARK_API_MOBILITHEK_NRW_DISABLED_STATIC_SUBSCRIPTION_ID',
        ]

    @staticmethod
    def test_get_static_parking_sites(
        nrw_disabled_pull_converter: NrwDisabledPullConverter,
        requests_mock: Mocker,
    ):
        requests_mock.get(
            'https://mobilithek.info:8443/mobilithek/api/v1.0/subscription/1111111111/clientPullService'
            '?subscriptionID=1111111111',
            text=get_data_path('nrw_disabled-static.json').read_text(),
        )

        static_parking_site_inputs, import_parking_site_exceptions = (
            nrw_disabled_pull_converter.get_static_parking_sites()
        )

        # The publication is JSON instead of the declared DATEX II 2.3 XML
        assert len(static_parking_site_inputs) == 0
        assert len(import_parking_site_exceptions) == 1
        assert 'Invalid XML' in import_parking_site_exceptions[0].message

    @staticmethod
    def test_get_realtime_parking_sites(nrw_disabled_pull_converter: NrwDisabledPullConverter):
        realtime_parking_site_inputs, import_parking_site_exceptions = (
            nrw_disabled_pull_converter.get_realtime_parking_sites()
        )

        assert len(realtime_parking_site_inputs) == 0
        assert len(import_parking_site_exceptions) == 0
