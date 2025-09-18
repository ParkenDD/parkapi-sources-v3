"""
Copyright 2025 binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

from pathlib import Path
from unittest.mock import Mock

import pytest
from requests_mock import Mocker

from parkapi_sources.converters import FreiburgScannerPullConverter
from parkapi_sources.util import RequestHelper
from tests.converters.helper import validate_static_parking_site_inputs


@pytest.fixture
def requests_mock_freiburg_scanner(requests_mock: Mocker) -> Mocker:
    json_path = Path(Path(__file__).parent, 'data', 'freiburg_scanner.geojson')
    with json_path.open() as json_file:
        json_data = json_file.read()

    requests_mock.get(
        'https://geoportal.freiburg.de/wfs/digit_parken/digit_parken?REQUEST=GetFeature&SRSNAME=EPSG:4326'
        '&SERVICE=WFS&VERSION=2.0.0&TYPENAMES=parkkartierung_mercedes_kanten&OUTPUTFORMAT=geojson',
        text=json_data,
    )

    return requests_mock


@pytest.fixture
def freiburg_scanner_pull_converter(
    mocked_config_helper: Mock, request_helper: RequestHelper
) -> FreiburgScannerPullConverter:
    return FreiburgScannerPullConverter(config_helper=mocked_config_helper, request_helper=request_helper)


class FreiburgScannerPullConverterTest:
    @staticmethod
    def test_get_static_parking_sites(
        freiburg_scanner_pull_converter: FreiburgScannerPullConverter,
        requests_mock_freiburg_scanner: Mocker,
    ):
        static_parking_site_inputs, import_parking_site_exceptions = (
            freiburg_scanner_pull_converter.get_static_parking_sites()
        )

        assert len(static_parking_site_inputs) == 144
        assert len(import_parking_site_exceptions) == 0

        validate_static_parking_site_inputs(static_parking_site_inputs)
