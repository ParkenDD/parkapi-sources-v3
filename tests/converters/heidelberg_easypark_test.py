"""
Copyright 2025 binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

from pathlib import Path
from unittest.mock import Mock

import pytest
from requests_mock import Mocker

from parkapi_sources.converters import HeidelbergEasyParkPullConverter
from parkapi_sources.util import RequestHelper
from tests.converters.helper import validate_static_parking_site_inputs


@pytest.fixture
def requests_mock_heidelberg_easypark(requests_mock: Mocker) -> Mocker:
    json_path = Path(Path(__file__).parent, 'data', 'heidelberg_easypark.geojson')
    with json_path.open() as json_file:
        json_data = json_file.read()

    requests_mock.get(
        'https://ckan.datenplattform.heidelberg.de/de/dataset/fecde4f4-41c0-4c3b-b763-41a84dad39f8/resource'
        '/12e9e778-880a-49a9-90cc-2fbb615f2da6/download/inventory_data_offset-1.json',
        text=json_data,
    )

    return requests_mock


@pytest.fixture
def heidelberg_easypark_pull_converter(
    mocked_config_helper: Mock, request_helper: RequestHelper
) -> HeidelbergEasyParkPullConverter:
    return HeidelbergEasyParkPullConverter(config_helper=mocked_config_helper, request_helper=request_helper)


class HeidelbergEasyparkPullConverterTest:
    @staticmethod
    def test_get_static_parking_sites(
        heidelberg_easypark_pull_converter: HeidelbergEasyParkPullConverter,
        requests_mock_heidelberg_easypark: Mocker,
    ):
        static_parking_site_inputs, import_parking_site_exceptions = (
            heidelberg_easypark_pull_converter.get_static_parking_sites()
        )

        assert len(static_parking_site_inputs) == 86
        assert len(import_parking_site_exceptions) == 0

        validate_static_parking_site_inputs(static_parking_site_inputs)
