"""
Copyright 2024 binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

from pathlib import Path
from unittest.mock import Mock

import pytest
from parkapi_sources.converters import HerrenbergBikePullConverter
from requests_mock import Mocker

from tests.converters.helper import validate_realtime_parking_site_inputs, validate_static_parking_site_inputs


@pytest.fixture
def requests_mock_herrenberg_bike(requests_mock: Mocker) -> Mocker:
    json_path = Path(Path(__file__).parent, 'data', 'herrenberg_bike.json')
    with json_path.open() as json_file:
        json_data = json_file.read()

    requests_mock.get('https://r2.munigrid.de/11-d76db68da7d8354bb425c9eb90d6d78a.json', text=json_data)

    return requests_mock


@pytest.fixture
def herrenberg_bike_pull_converter(mocked_config_helper: Mock) -> HerrenbergBikePullConverter:
    return HerrenbergBikePullConverter(config_helper=mocked_config_helper)


class HerrenbergBikePullConverterTest:
    @staticmethod
    def test_get_static_parking_sites(herrenberg_bike_pull_converter: HerrenbergBikePullConverter, requests_mock_herrenberg_bike: Mocker):
        static_parking_site_inputs, import_parking_site_exceptions = herrenberg_bike_pull_converter.get_static_parking_sites()

        assert len(static_parking_site_inputs) == 170
        # For missing capacities
        assert len(import_parking_site_exceptions) == 14

        validate_static_parking_site_inputs(static_parking_site_inputs)

    @staticmethod
    def test_get_realtime_parking_sites(herrenberg_bike_pull_converter: HerrenbergBikePullConverter, requests_mock_herrenberg_bike: Mocker):
        realtime_parking_site_inputs, import_parking_site_exceptions = herrenberg_bike_pull_converter.get_realtime_parking_sites()

        assert len(realtime_parking_site_inputs) == 0
        assert len(import_parking_site_exceptions) == 0

        validate_realtime_parking_site_inputs(realtime_parking_site_inputs)
