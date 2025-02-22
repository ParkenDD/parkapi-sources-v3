"""
Copyright 2024 binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

from pathlib import Path
from unittest.mock import Mock

import pytest
from requests_mock import Mocker

from parkapi_sources.converters import HerrenbergBikePullConverter
from parkapi_sources.util import RequestHelper
from tests.converters.helper import validate_realtime_parking_site_inputs, validate_static_parking_site_inputs


@pytest.fixture
def requests_mock_herrenberg_bike(requests_mock: Mocker) -> Mocker:
    json_path = Path(Path(__file__).parent, 'data', 'herrenberg_bike.json')
    with json_path.open() as json_file:
        json_data = json_file.read()

    requests_mock.get('https://www.munigrid.de/api/file/11/latest', text=json_data)

    return requests_mock


@pytest.fixture
def herrenberg_bike_config_helper(mocked_config_helper: Mock):
    config = {}
    mocked_config_helper.get.side_effect = lambda key, default=None: config.get(key, default)
    return mocked_config_helper


@pytest.fixture
def herrenberg_bike_pull_converter(
    herrenberg_bike_config_helper: Mock,
    request_helper: RequestHelper,
) -> HerrenbergBikePullConverter:
    return HerrenbergBikePullConverter(config_helper=herrenberg_bike_config_helper, request_helper=request_helper)


@pytest.fixture
def herrenberg_bike_ignore_missing_capacity_config_helper(mocked_config_helper: Mock):
    config = {
        'PARK_API_HERRENBERG_BIKE_IGNORE_MISSING_CAPACITIES': True,
    }
    mocked_config_helper.get.side_effect = lambda key, default=None: config.get(key, default)
    return mocked_config_helper


@pytest.fixture
def herrenberg_bike_ignore_missing_capacity_pull_converter(
    herrenberg_bike_ignore_missing_capacity_config_helper: Mock,
    request_helper: RequestHelper,
) -> HerrenbergBikePullConverter:
    return HerrenbergBikePullConverter(
        config_helper=herrenberg_bike_ignore_missing_capacity_config_helper,
        request_helper=request_helper,
    )


class HerrenbergBikePullConverterTest:
    @staticmethod
    def test_get_static_parking_sites(
        herrenberg_bike_pull_converter: HerrenbergBikePullConverter, requests_mock_herrenberg_bike: Mocker
    ):
        static_parking_site_inputs, import_parking_site_exceptions = (
            herrenberg_bike_pull_converter.get_static_parking_sites()
        )

        assert len(static_parking_site_inputs) == 184
        assert len(import_parking_site_exceptions) == 0

        validate_static_parking_site_inputs(static_parking_site_inputs)

    @staticmethod
    def test_get_static_parking_sites_ignore_missing_capacities(
        herrenberg_bike_ignore_missing_capacity_pull_converter: HerrenbergBikePullConverter,
        requests_mock_herrenberg_bike: Mocker,
    ):
        static_parking_site_inputs, import_parking_site_exceptions = (
            herrenberg_bike_ignore_missing_capacity_pull_converter.get_static_parking_sites()
        )

        assert len(static_parking_site_inputs) == 184
        assert len(import_parking_site_exceptions) == 0

        validate_static_parking_site_inputs(static_parking_site_inputs)

    @staticmethod
    def test_get_realtime_parking_sites(
        herrenberg_bike_pull_converter: HerrenbergBikePullConverter, requests_mock_herrenberg_bike: Mocker
    ):
        realtime_parking_site_inputs, import_parking_site_exceptions = (
            herrenberg_bike_pull_converter.get_realtime_parking_sites()
        )

        assert len(realtime_parking_site_inputs) == 0
        assert len(import_parking_site_exceptions) == 0

        validate_realtime_parking_site_inputs(realtime_parking_site_inputs)
