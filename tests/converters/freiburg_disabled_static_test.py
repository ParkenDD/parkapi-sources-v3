"""
Copyright 2025 binary butterfly GmbH
Use of this source code is governed by an MIT-style license that can be found in the LICENSE.txt.
"""

from pathlib import Path
from unittest.mock import Mock

import pytest
from requests_mock import Mocker

from parkapi_sources.converters import FreiburgDisabledStaticPullConverter
from parkapi_sources.util import RequestHelper
from tests.converters.helper import validate_static_parking_spot_inputs


@pytest.fixture
def freiburg_disabled_static_pull_converter(
    mocked_config_helper: Mock,
    request_helper: RequestHelper,
) -> FreiburgDisabledStaticPullConverter:
    return FreiburgDisabledStaticPullConverter(
        config_helper=mocked_config_helper,
        request_helper=request_helper,
    )


@pytest.fixture
def requests_mock_freiburg_disabled_sensors(requests_mock: Mocker) -> Mocker:
    json_path = Path(Path(__file__).parent, 'data', 'freiburg_disabled_static.geojson')
    with json_path.open() as json_file:
        json_data = json_file.read()

    requests_mock.get(
        'https://geoportal.freiburg.de/wms/gut_parken/gut_parken?SERVICE=WFS&REQUEST=GetFeature&SRSNAME=EPSG:4326'
        '&SERVICE=WFS&VERSION=2.0.0&TYPENAMES=behindertenparkplatz_detail&OUTPUTFORMAT=geojson',
        text=json_data,
    )

    return requests_mock


class FreiburgDisabledStaticConverterTest:
    @staticmethod
    def test_get_static_parking_spots(
        freiburg_disabled_static_pull_converter: FreiburgDisabledStaticPullConverter,
        requests_mock_freiburg_disabled_sensors: Mocker,
    ):
        static_parking_spot_inputs, import_parking_spot_exceptions = (
            freiburg_disabled_static_pull_converter.get_static_parking_spots()
        )

        assert len(static_parking_spot_inputs) == 312
        assert len(import_parking_spot_exceptions) == 0

        validate_static_parking_spot_inputs(static_parking_spot_inputs)
