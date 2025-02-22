"""
Copyright 2024 binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

from pathlib import Path
from unittest.mock import Mock

import pytest
from requests_mock import Mocker

from parkapi_sources.converters import KarlsruhePullConverter
from parkapi_sources.util import RequestHelper
from tests.converters.helper import validate_realtime_parking_site_inputs, validate_static_parking_site_inputs


@pytest.fixture
def requests_mock_karlsruhe(requests_mock: Mocker) -> Mocker:
    json_path = Path(Path(__file__).parent, 'data', 'karlsruhe.json')
    with json_path.open() as json_file:
        json_data = json_file.read()

    requests_mock.get('https://mobil.trk.de/geoserver/TBA/ows', text=json_data)

    return requests_mock


@pytest.fixture
def karlsruhe_pull_converter(mocked_config_helper: Mock, request_helper: RequestHelper) -> KarlsruhePullConverter:
    return KarlsruhePullConverter(config_helper=mocked_config_helper, request_helper=request_helper)


class KarlsruhePullConverterTest:
    @staticmethod
    def test_get_static_parking_sites(
        karlsruhe_pull_converter: KarlsruhePullConverter,
        requests_mock_karlsruhe: Mocker,
    ):
        static_parking_site_inputs, import_parking_site_exceptions = karlsruhe_pull_converter.get_static_parking_sites()

        assert len(static_parking_site_inputs) == 75
        assert len(import_parking_site_exceptions) == 15

        validate_static_parking_site_inputs(static_parking_site_inputs)

    @staticmethod
    def test_get_realtime_parking_sites(
        karlsruhe_pull_converter: KarlsruhePullConverter,
        requests_mock_karlsruhe: Mocker,
    ):
        realtime_parking_site_inputs, import_parking_site_exceptions = (
            karlsruhe_pull_converter.get_realtime_parking_sites()
        )

        assert len(realtime_parking_site_inputs) == 39
        assert len(import_parking_site_exceptions) == 15

        validate_realtime_parking_site_inputs(realtime_parking_site_inputs)
