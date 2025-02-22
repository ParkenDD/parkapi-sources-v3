"""
Copyright 2024 binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

from pathlib import Path
from unittest.mock import Mock

import pytest
from requests_mock import Mocker

from parkapi_sources.converters import KarlsruheBikePullConverter
from parkapi_sources.util import RequestHelper
from tests.converters.helper import validate_realtime_parking_site_inputs, validate_static_parking_site_inputs


@pytest.fixture
def requests_mock_karlsruhe_bike(requests_mock: Mocker) -> Mocker:
    json_path = Path(Path(__file__).parent, 'data', 'karlsruhe_bike.json')
    with json_path.open() as json_file:
        json_data = json_file.read()

    requests_mock.get('https://mobil.trk.de/geoserver/TBA/ows', text=json_data)

    return requests_mock


@pytest.fixture
def karlsruhe_bike_config_helper(mocked_config_helper: Mock):
    config = {}
    mocked_config_helper.get.side_effect = lambda key, default=None: config.get(key, default)
    return mocked_config_helper


@pytest.fixture
def karlsruhe_bike_pull_converter(
    karlsruhe_bike_config_helper: Mock,
    request_helper: RequestHelper,
) -> KarlsruheBikePullConverter:
    return KarlsruheBikePullConverter(config_helper=karlsruhe_bike_config_helper, request_helper=request_helper)


@pytest.fixture
def karlsruhe_bike_ignore_missing_capacity_config_helper(mocked_config_helper: Mock):
    config = {
        'PARK_API_KARLSRUHE_BIKE_IGNORE_MISSING_CAPACITIES': True,
    }
    mocked_config_helper.get.side_effect = lambda key, default=None: config.get(key, default)
    return mocked_config_helper


@pytest.fixture
def karlsruhe_bike_ignore_missing_capacity_pull_converter(
    karlsruhe_bike_ignore_missing_capacity_config_helper: Mock,
    request_helper: RequestHelper,
) -> KarlsruheBikePullConverter:
    return KarlsruheBikePullConverter(
        config_helper=karlsruhe_bike_ignore_missing_capacity_config_helper,
        request_helper=request_helper,
    )


class KarlsruheBikePullConverterTest:
    @staticmethod
    def test_get_static_parking_sites(
        karlsruhe_bike_pull_converter: KarlsruheBikePullConverter, requests_mock_karlsruhe_bike: Mocker
    ):
        static_parking_site_inputs, import_parking_site_exceptions = (
            karlsruhe_bike_pull_converter.get_static_parking_sites()
        )

        assert len(static_parking_site_inputs) == 296
        # Lots of missing capacities
        assert len(import_parking_site_exceptions) == 483

        validate_static_parking_site_inputs(static_parking_site_inputs)

    @staticmethod
    def test_get_static_parking_sites_ignore_missing_capacities(
        karlsruhe_bike_ignore_missing_capacity_pull_converter: KarlsruheBikePullConverter,
        requests_mock_karlsruhe_bike: Mocker,
    ):
        static_parking_site_inputs, import_parking_site_exceptions = (
            karlsruhe_bike_ignore_missing_capacity_pull_converter.get_static_parking_sites()
        )

        assert len(static_parking_site_inputs) == 296
        assert len(import_parking_site_exceptions) == 0

        validate_static_parking_site_inputs(static_parking_site_inputs)

    @staticmethod
    def test_get_realtime_parking_sites(
        karlsruhe_bike_pull_converter: KarlsruheBikePullConverter,
        requests_mock_karlsruhe_bike: Mocker,
    ):
        realtime_parking_site_inputs, import_parking_site_exceptions = (
            karlsruhe_bike_pull_converter.get_realtime_parking_sites()
        )

        assert len(realtime_parking_site_inputs) == 0
        assert len(import_parking_site_exceptions) == 0

        validate_realtime_parking_site_inputs(realtime_parking_site_inputs)
