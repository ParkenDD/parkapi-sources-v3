"""
Copyright 2024 binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

from pathlib import Path
from unittest.mock import Mock

import pytest
from requests_mock import Mocker

from parkapi_sources.converters.ulm import UlmPullConverter
from parkapi_sources.util import RequestHelper
from tests.converters.helper import validate_realtime_parking_site_inputs, validate_static_parking_site_inputs


@pytest.fixture
def ulm_pull_converter(mocked_static_geojson_config_helper: Mock, request_helper: RequestHelper) -> UlmPullConverter:
    return UlmPullConverter(config_helper=mocked_static_geojson_config_helper, request_helper=request_helper)


class UlmPullConverterTest:
    @staticmethod
    def test_get_static_parking_sites(ulm_pull_converter: UlmPullConverter):
        static_parking_site_inputs, import_parking_site_exceptions = ulm_pull_converter.get_static_parking_sites()

        assert len(static_parking_site_inputs) == 10
        assert len(import_parking_site_exceptions) == 0

        validate_static_parking_site_inputs(static_parking_site_inputs)

    @staticmethod
    def test_get_realtime_parking_sites(ulm_pull_converter: UlmPullConverter, requests_mock: Mocker):
        html_path = Path(Path(__file__).parent, 'data', 'ulm.html')
        with html_path.open() as html_file:
            html_data = html_file.read()

        requests_mock.get('https://www.parken-in-ulm.de', text=html_data)

        realtime_parking_site_inputs, import_parking_site_exceptions = ulm_pull_converter.get_realtime_parking_sites()
        assert len(realtime_parking_site_inputs) == 10
        assert len(import_parking_site_exceptions) == 0

        validate_realtime_parking_site_inputs(realtime_parking_site_inputs)
