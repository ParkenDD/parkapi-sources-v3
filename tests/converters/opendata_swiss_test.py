"""
Copyright 2024 binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

from pathlib import Path
from unittest.mock import Mock

import pytest
from parkapi_sources.converters import OpenDataSwissPullConverter
from requests_mock import Mocker

from tests.converters.helper import validate_static_parking_site_inputs


@pytest.fixture
def requests_mock_opendata_swiss(requests_mock: Mocker) -> Mocker:
    json_path = Path(Path(__file__).parent, 'data', 'opendata_swiss.json')
    with json_path.open() as json_file:
        json_data = json_file.read()

    requests_mock.get(
        'https://opentransportdata.swiss/dataset/c1be030e-adad-41c6-8ee2-899e85f840f6/resource/5dab3aba-6b5a-42cb-bb73-103fb28c7e10/download/parking-facilities.json',
        text=json_data,
    )

    return requests_mock


@pytest.fixture
def opendata_swiss_pull_converter(mocked_config_helper: Mock) -> OpenDataSwissPullConverter:
    return OpenDataSwissPullConverter(config_helper=mocked_config_helper)


class OpenDataSwissPullConverterTest:
    @staticmethod
    def test_get_static_parking_sites(opendata_swiss_pull_converter: OpenDataSwissPullConverter, requests_mock_opendata_swiss: Mocker):
        static_parking_site_inputs, import_parking_site_exceptions = opendata_swiss_pull_converter.get_static_parking_sites()

        assert len(static_parking_site_inputs) > len(
            import_parking_site_exceptions
        ), 'There should be more valid then invalid parking sites'

        validate_static_parking_site_inputs(static_parking_site_inputs)
