"""
Copyright 2024 binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

from pathlib import Path
from unittest.mock import Mock

import pytest
from requests_mock import Mocker

from parkapi_sources.converters import AalenPullConverter
from parkapi_sources.util import RequestHelper
from tests.converters.helper import validate_realtime_parking_site_inputs, validate_static_parking_site_inputs


@pytest.fixture
def aalen_pull_converter(
    mocked_static_geojson_config_helper: Mock,
    request_helper: RequestHelper,
) -> AalenPullConverter:
    return AalenPullConverter(config_helper=mocked_static_geojson_config_helper, request_helper=request_helper)


def aalen_request_mocked_json(requests_mock: Mocker, filename: str):
    # We need to get GeoJSON data
    requests_mock.real_http = True

    json_path = Path(Path(__file__).parent, 'data', filename)
    with json_path.open() as json_file:
        json_data = json_file.read()

    requests_mock.get(
        'https://www.sw-aalen.de/privatkunden/dienstleistungen/parken/parkhausbelegung.json', text=json_data
    )


class AalenPullConverterTest:
    @staticmethod
    def test_get_static_parking_sites(aalen_pull_converter: AalenPullConverter):
        static_parking_site_inputs, import_parking_site_exceptions = aalen_pull_converter.get_static_parking_sites()

        assert len(static_parking_site_inputs) == 6
        assert len(import_parking_site_exceptions) == 0

        validate_static_parking_site_inputs(static_parking_site_inputs)

    @staticmethod
    def test_get_realtime_parking_sites(aalen_pull_converter: AalenPullConverter, requests_mock: Mocker):
        aalen_request_mocked_json(requests_mock, 'aalen.json')

        realtime_parking_site_inputs, import_parking_site_exceptions = aalen_pull_converter.get_realtime_parking_sites()

        assert len(realtime_parking_site_inputs) == 6
        assert len(import_parking_site_exceptions) == 0

        validate_realtime_parking_site_inputs(realtime_parking_site_inputs)
