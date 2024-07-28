"""
Copyright 2025 binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

from pathlib import Path
from unittest.mock import Mock

import pytest
from requests_mock import Mocker

from parkapi_sources.converters.basel import BaselPullConverter
from parkapi_sources.util import RequestHelper
from tests.converters.helper import validate_realtime_parking_site_inputs, validate_static_parking_site_inputs


@pytest.fixture
def basel_pull_converter(
    mocked_config_helper: Mock, request_helper: RequestHelper, requests_mock: Mocker
) -> BaselPullConverter:
    json_path = Path(Path(__file__).parent, 'data', 'basel.json')
    with json_path.open() as json_file:
        json_data = json_file.read()

    requests_mock.get('https://data.bs.ch/api/v2/catalog/datasets/100088/exports/json', text=json_data)

    return BaselPullConverter(config_helper=mocked_config_helper, request_helper=request_helper)


class BaselPullConverterTest:
    @staticmethod
    def test_get_static_parking_sites(basel_pull_converter: BaselPullConverter):
        static_parking_site_inputs, import_parking_site_exceptions = basel_pull_converter.get_static_parking_sites()

        assert len(static_parking_site_inputs) == 16
        assert len(import_parking_site_exceptions) == 1

        validate_static_parking_site_inputs(static_parking_site_inputs)

    @staticmethod
    def test_get_realtime_parking_sites(basel_pull_converter: BaselPullConverter):
        realtime_parking_site_inputs, import_parking_site_exceptions = basel_pull_converter.get_realtime_parking_sites()

        assert len(realtime_parking_site_inputs) == 16
        assert len(import_parking_site_exceptions) == 1

        validate_realtime_parking_site_inputs(realtime_parking_site_inputs)
