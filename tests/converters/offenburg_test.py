"""
Copyright 2026 binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

from unittest.mock import Mock

import pytest
from requests_mock import Mocker
from syrupy.assertion import SnapshotAssertion

from parkapi_sources.converters import OffenburgPullConverter
from parkapi_sources.util import RequestHelper
from tests.converters.helper import (
    get_data_path,
    validate_realtime_parking_site_inputs,
    validate_static_parking_site_inputs,
)

STATIC_URL = (
    'https://mobilithek.info:8443/mobilithek/api/v1.0/subscription/1111111111/clientPullService'
    '?subscriptionID=1111111111'
)
REALTIME_URL = (
    'https://mobilithek.info:8443/mobilithek/api/v1.0/subscription/2222222222/clientPullService'
    '?subscriptionID=2222222222'
)


def get_offenburg_config(ignore_missing_capacities: bool | None) -> dict:
    config = {
        'PARK_API_MOBILITHEK_CERT': '/dev/null',
        'PARK_API_MOBILITHEK_KEY': '/dev/null',
        'PARK_API_MOBILITHEK_OFFENBURG_STATIC_SUBSCRIPTION_ID': 1111111111,
        'PARK_API_MOBILITHEK_OFFENBURG_REALTIME_SUBSCRIPTION_ID': 2222222222,
    }
    if ignore_missing_capacities is not None:
        config['PARK_API_OFFENBURG_IGNORE_MISSING_CAPACITIES'] = ignore_missing_capacities
    return config


@pytest.fixture
def offenburg_pull_converter(
    mocked_config_helper: Mock,
    request_helper: RequestHelper,
) -> OffenburgPullConverter:
    config = get_offenburg_config(ignore_missing_capacities=None)
    mocked_config_helper.get.side_effect = lambda key, default=None: config.get(key, default)
    return OffenburgPullConverter(config_helper=mocked_config_helper, request_helper=request_helper)


@pytest.fixture
def offenburg_not_ignore_missing_capacities_pull_converter(
    mocked_config_helper: Mock,
    request_helper: RequestHelper,
) -> OffenburgPullConverter:
    config = get_offenburg_config(ignore_missing_capacities=False)
    mocked_config_helper.get.side_effect = lambda key, default=None: config.get(key, default)
    return OffenburgPullConverter(config_helper=mocked_config_helper, request_helper=request_helper)


class OffenburgPullConverterTest:
    @staticmethod
    def test_get_static_parking_sites(
        offenburg_pull_converter: OffenburgPullConverter,
        requests_mock: Mocker,
        snapshot: SnapshotAssertion,
    ):
        requests_mock.get(STATIC_URL, text=get_data_path('offenburg-static.xml').read_text())

        static_parking_site_inputs, import_parking_site_exceptions = offenburg_pull_converter.get_static_parking_sites()

        assert len(static_parking_site_inputs) == 5
        assert len(import_parking_site_exceptions) == 0

        validate_static_parking_site_inputs(static_parking_site_inputs, snapshot)

    @staticmethod
    def test_get_static_parking_sites_not_ignore_missing_capacities(
        offenburg_not_ignore_missing_capacities_pull_converter: OffenburgPullConverter,
        requests_mock: Mocker,
    ):
        requests_mock.get(STATIC_URL, text=get_data_path('offenburg-static.xml').read_text())

        static_parking_site_inputs, import_parking_site_exceptions = (
            offenburg_not_ignore_missing_capacities_pull_converter.get_static_parking_sites()
        )

        assert len(static_parking_site_inputs) == 5
        assert len(import_parking_site_exceptions) == 3

    @staticmethod
    def test_get_realtime_parking_sites(
        offenburg_pull_converter: OffenburgPullConverter,
        requests_mock: Mocker,
        snapshot: SnapshotAssertion,
    ):
        requests_mock.get(STATIC_URL, text=get_data_path('offenburg-static.xml').read_text())
        requests_mock.get(REALTIME_URL, text=get_data_path('offenburg-realtime.xml').read_text())

        realtime_parking_site_inputs, import_parking_site_exceptions = (
            offenburg_pull_converter.get_realtime_parking_sites()
        )

        assert len(realtime_parking_site_inputs) == 5
        assert len(import_parking_site_exceptions) == 0

        validate_realtime_parking_site_inputs(realtime_parking_site_inputs, snapshot)

    @staticmethod
    def test_get_realtime_parking_sites_not_ignore_missing_capacities(
        offenburg_not_ignore_missing_capacities_pull_converter: OffenburgPullConverter,
        requests_mock: Mocker,
    ):
        requests_mock.get(REALTIME_URL, text=get_data_path('offenburg-realtime.xml').read_text())

        realtime_parking_site_inputs, import_parking_site_exceptions = (
            offenburg_not_ignore_missing_capacities_pull_converter.get_realtime_parking_sites()
        )

        assert len(realtime_parking_site_inputs) == 8
        assert len(import_parking_site_exceptions) == 0
