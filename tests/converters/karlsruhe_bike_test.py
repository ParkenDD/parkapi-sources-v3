"""
Copyright 2024 binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

from pathlib import Path
from unittest.mock import Mock

import pytest
from parkapi_sources.converters import KarlsruheBikePullConverter
from requests_mock import Mocker

from tests.converters.helper import validate_realtime_parking_site_inputs, validate_static_parking_site_inputs


@pytest.fixture
def requests_mock_karlsruhe_bike(requests_mock: Mocker) -> Mocker:
    json_path = Path(Path(__file__).parent, 'data', 'karlsruhe_bike.json')
    with json_path.open() as json_file:
        json_data = json_file.read()

    requests_mock.get('https://mobil.trk.de:8443/geoserver/TBA/ows', text=json_data)

    return requests_mock


@pytest.fixture
def karlsruhe_bike_pull_converter(mocked_config_helper: Mock) -> KarlsruheBikePullConverter:
    return KarlsruheBikePullConverter(config_helper=mocked_config_helper)


class KarlsruheBikePullConverterTest:
    @staticmethod
    def test_get_static_parking_sites(karlsruhe_bike_pull_converter: KarlsruheBikePullConverter, requests_mock_karlsruhe_bike: Mocker):
        static_parking_site_inputs, import_parking_site_exceptions = karlsruhe_bike_pull_converter.get_static_parking_sites()

        assert len(static_parking_site_inputs) == 154
        # Lots of missing capacities
        assert len(import_parking_site_exceptions) == 460

        validate_static_parking_site_inputs(static_parking_site_inputs)

    @staticmethod
    def test_get_realtime_parking_sites(karlsruhe_bike_pull_converter: KarlsruheBikePullConverter, requests_mock_karlsruhe_bike: Mocker):
        realtime_parking_site_inputs, import_parking_site_exceptions = karlsruhe_bike_pull_converter.get_realtime_parking_sites()

        assert len(realtime_parking_site_inputs) == 0
        assert len(import_parking_site_exceptions) == 0

        validate_realtime_parking_site_inputs(realtime_parking_site_inputs)
