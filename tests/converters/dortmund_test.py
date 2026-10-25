"""
Copyright 2026 binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

from unittest.mock import Mock

import pytest
from requests_mock import Mocker
from syrupy.assertion import SnapshotAssertion

from parkapi_sources.converters import DortmundPullConverter
from parkapi_sources.util import RequestHelper
from tests.converters.helper import (
    get_data_path,
    validate_realtime_parking_site_inputs,
    validate_static_parking_site_inputs,
)


@pytest.fixture
def dortmund_config_helper(mocked_config_helper: Mock):
    config = {
        'PARK_API_MOBILITHEK_CERT': '/dev/null',
        'PARK_API_MOBILITHEK_KEY': '/dev/null',
        'PARK_API_MOBILITHEK_DORTMUND_STATIC_SUBSCRIPTION_ID': 1111111111,
        'PARK_API_MOBILITHEK_DORTMUND_REALTIME_SUBSCRIPTION_ID': 2222222222,
    }
    mocked_config_helper.get.side_effect = lambda key, default=None: config.get(key, default)
    return mocked_config_helper


@pytest.fixture
def dortmund_pull_converter(
    dortmund_config_helper: Mock,
    request_helper: RequestHelper,
) -> DortmundPullConverter:
    return DortmundPullConverter(config_helper=dortmund_config_helper, request_helper=request_helper)


class DortmundPullConverterTest:
    @staticmethod
    def test_get_static_parking_sites(
        dortmund_pull_converter: DortmundPullConverter,
        requests_mock: Mocker,
        snapshot: SnapshotAssertion,
    ):
        requests_mock.get(
            'https://mobilithek.info:8443/mobilithek/api/v1.0/container/subscription?subscriptionID=1111111111',
            text=get_data_path('dortmund-static.xml').read_text(),
        )

        static_parking_site_inputs, import_parking_site_exceptions = dortmund_pull_converter.get_static_parking_sites()

        assert len(static_parking_site_inputs) == 3
        assert len(import_parking_site_exceptions) == 0

        validate_static_parking_site_inputs(static_parking_site_inputs, snapshot)

    @staticmethod
    def test_get_realtime_parking_sites(
        dortmund_pull_converter: DortmundPullConverter,
        requests_mock: Mocker,
        snapshot: SnapshotAssertion,
    ):
        requests_mock.get(
            'https://mobilithek.info:8443/mobilithek/api/v1.0/container/subscription?subscriptionID=2222222222',
            text=get_data_path('dortmund-realtime.xml').read_text(),
        )

        realtime_parking_site_inputs, import_parking_site_exceptions = (
            dortmund_pull_converter.get_realtime_parking_sites()
        )

        assert len(realtime_parking_site_inputs) == 3
        assert len(import_parking_site_exceptions) == 0

        validate_realtime_parking_site_inputs(realtime_parking_site_inputs, snapshot)
