"""
Copyright 2025 binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

from pathlib import Path
from unittest.mock import Mock

import pytest
from requests_mock import Mocker

from parkapi_sources.converters.jena import JenaPullConverter
from parkapi_sources.util import RequestHelper
from tests.converters.helper import validate_static_parking_site_inputs


@pytest.fixture
def jena_pull_converter(mocked_config_helper: Mock, request_helper: RequestHelper) -> JenaPullConverter:
    return JenaPullConverter(config_helper=mocked_config_helper, request_helper=request_helper)


class JenaPullConverterTest:
    @staticmethod
    def test_get_static_parking_sites(jena_pull_converter: JenaPullConverter, requests_mock: Mocker):
        json_path = Path(Path(__file__).parent, 'data', 'jena.geojson')
        with json_path.open() as json_file:
            json_data = json_file.read()

        requests_mock.get('https://opendata.jena.de/data/parken.geojson', text=json_data)

        static_parking_site_inputs, import_parking_site_exceptions = jena_pull_converter.get_static_parking_sites()

        assert len(static_parking_site_inputs) == 103
        assert len(import_parking_site_exceptions) == 0

        validate_static_parking_site_inputs(static_parking_site_inputs)
